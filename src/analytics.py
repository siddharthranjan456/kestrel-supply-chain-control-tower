from src.database import query


def service_orders(start_date: str, end_date: str):
    sql = """
    WITH eligible_orders AS (
      SELECT o.* FROM orders o JOIN outlets x ON x.outlet_id=o.outlet_id
      WHERE o.order_date BETWEEN ? AND ? AND o.order_status IN ('DELIVERED','PARTIAL')
        AND x.is_deleted=0 AND x.status='ACTIVE'
        AND UPPER(x.outlet_name) NOT LIKE '%TEST%' AND UPPER(x.outlet_name) NOT LIKE '%MIGRATION%'
    ), line_metrics AS (
      SELECT ol.order_id,
        SUM(CASE WHEN UPPER(ol.qty_uom)='CASE' THEN ol.ordered_qty*ol.case_pack_at_order ELSE ol.ordered_qty END) ordered_eaches,
        SUM(CASE WHEN UPPER(ol.qty_uom)='CASE' THEN ol.delivered_qty*ol.case_pack_at_order ELSE ol.delivered_qty END) delivered_eaches,
        SUM(CASE WHEN UPPER(ol.qty_uom)='CASE' THEN ol.ordered_qty ELSE ol.ordered_qty/NULLIF(ol.case_pack_at_order,0) END) ordered_cases,
        SUM(CASE WHEN UPPER(ol.qty_uom)='CASE' THEN ol.delivered_qty ELSE ol.delivered_qty/NULLIF(ol.case_pack_at_order,0) END) delivered_cases
      FROM order_lines ol JOIN eligible_orders eo ON eo.order_id=ol.order_id GROUP BY ol.order_id
    ), delivery_metrics AS (
      SELECT order_id, MAX(delay_minutes) max_delay_minutes,
        MAX(temperature_excursion_flag) excursion,
        MAX(actual_arrival) actual_arrival
      FROM deliveries GROUP BY order_id
    )
    SELECT o.order_id,o.order_date,o.channel,r.region_name region,
      w.warehouse_name warehouse,rt.route_code,rt.route_name,
      x.outlet_code,x.outlet_name,x.city,
      lm.ordered_eaches,lm.delivered_eaches,lm.ordered_cases,lm.delivered_cases,
      COALESCE(dm.max_delay_minutes,999999) max_delay_minutes,
      CASE WHEN COALESCE(dm.max_delay_minutes,999999)<=0
             AND lm.delivered_eaches>=lm.ordered_eaches THEN 1 ELSE 0 END otif
    FROM eligible_orders o
    JOIN line_metrics lm ON lm.order_id=o.order_id
    JOIN outlets x ON x.outlet_id=o.outlet_id
    JOIN regions r ON r.region_id=o.region_id
    JOIN warehouses w ON w.warehouse_id=o.warehouse_id
    JOIN routes rt ON rt.route_id=o.route_id
    LEFT JOIN delivery_metrics dm ON dm.order_id=o.order_id
    """
    return query(sql, (start_date, end_date))


def cold_chain_deliveries(start_date: str, end_date: str):
    deliveries_sql = """
    SELECT d.delivery_id,d.order_id,o.order_date,r.region_name region,w.warehouse_name warehouse,
      rt.route_code,rt.route_name,d.delay_minutes,d.temperature_excursion_flag,
      d.max_temp_celsius,d.delivery_status
    FROM deliveries d
    JOIN orders o ON o.order_id=d.order_id
    JOIN outlets x ON x.outlet_id=o.outlet_id AND x.is_deleted=0
    JOIN regions r ON r.region_id=o.region_id
    JOIN warehouses w ON w.warehouse_id=o.warehouse_id
    JOIN routes rt ON rt.route_id=o.route_id
    WHERE o.order_date BETWEEN ? AND ? AND o.order_status IN ('DELIVERED','PARTIAL')
    """
    chilled_sql = """
    SELECT DISTINCT ol.order_id
    FROM order_lines ol JOIN products p ON p.product_id=ol.product_id AND p.is_chilled=1
    JOIN orders o ON o.order_id=ol.order_id
    WHERE o.order_date BETWEEN ? AND ? AND o.order_status IN ('DELIVERED','PARTIAL')
    """
    deliveries = query(deliveries_sql, (start_date, end_date))
    chilled_orders = query(chilled_sql, (start_date, end_date))
    return deliveries.merge(chilled_orders, on="order_id", how="inner")


def near_expiry(end_date: str, days: int = 30):
    sql = """
    WITH latest AS (SELECT MAX(snapshot_date) snapshot_date FROM inventory_snapshots WHERE snapshot_date<=?)
    SELECT i.snapshot_date,w.warehouse_name,p.sku_code,p.product_name,p.category,
      i.batch_id,i.available_cases,i.expiry_date,
      CAST(julianday(i.expiry_date)-julianday(i.snapshot_date) AS INTEGER) days_to_expiry,
      i.available_cases*p.case_pack*p.list_price_inr estimated_trade_value_inr
    FROM inventory_snapshots i
    JOIN latest l ON l.snapshot_date=i.snapshot_date
    JOIN products p ON p.product_id=i.product_id
    JOIN warehouses w ON w.warehouse_id=i.warehouse_id
    WHERE i.available_cases>0
      AND julianday(i.expiry_date)-julianday(i.snapshot_date) BETWEEN 0 AND ?
    ORDER BY estimated_trade_value_inr DESC
    """
    return query(sql, (end_date, days))


def returns_data(start_date: str, end_date: str):
    sql = """
    SELECT rc.return_id,rc.return_date,r.region_name region,w.warehouse_name warehouse,
      p.category,p.sku_code,p.product_name,rc.return_reason_code,rc.disposition,rc.status,
      ABS(rc.return_qty) return_qty,
      CASE WHEN UPPER(rc.qty_uom)='CASE' THEN ABS(rc.return_qty)*ol.case_pack_at_order ELSE ABS(rc.return_qty) END returned_eaches,
      ABS(rc.credit_note_value_inr) credit_note_value_inr
    FROM returns_credit_notes rc
    JOIN orders o ON o.order_id=rc.order_id
    JOIN order_lines ol ON ol.order_line_id=rc.order_line_id
    JOIN products p ON p.product_id=rc.product_id
    JOIN regions r ON r.region_id=o.region_id
    JOIN warehouses w ON w.warehouse_id=o.warehouse_id
    JOIN outlets x ON x.outlet_id=o.outlet_id
    WHERE rc.return_date BETWEEN ? AND ? AND x.is_deleted=0
    """
    return query(sql, (start_date, end_date))


def delivered_cases_by_warehouse(start_date: str, end_date: str):
    sql = """
    SELECT w.warehouse_code,w.warehouse_name,
      SUM(CASE WHEN UPPER(ol.qty_uom)='CASE' THEN ol.delivered_qty ELSE ol.delivered_qty/NULLIF(ol.case_pack_at_order,0) END) delivered_cases
    FROM orders o JOIN order_lines ol ON ol.order_id=o.order_id
    JOIN warehouses w ON w.warehouse_id=o.warehouse_id
    JOIN outlets x ON x.outlet_id=o.outlet_id
    WHERE o.order_date BETWEEN ? AND ? AND o.order_status IN ('DELIVERED','PARTIAL') AND x.is_deleted=0
    GROUP BY w.warehouse_code,w.warehouse_name
    """
    return query(sql, (start_date, end_date))


def top_skus(start_date: str, end_date: str, limit: int = 20):
    sql = """
    SELECT p.product_id,p.sku_code,p.product_name,p.brand,p.category,p.pack_size_value,p.pack_size_uom,p.mrp_inr,
      SUM(ol.line_value_inr) sales_value_inr
    FROM orders o JOIN order_lines ol ON ol.order_id=o.order_id
    JOIN products p ON p.product_id=ol.product_id
    JOIN outlets x ON x.outlet_id=o.outlet_id
    WHERE o.order_date BETWEEN ? AND ? AND o.order_status IN ('DELIVERED','PARTIAL') AND x.is_deleted=0
    GROUP BY p.product_id ORDER BY sales_value_inr DESC LIMIT ?
    """
    return query(sql, (start_date, end_date, limit))
