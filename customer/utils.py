"""Utilities for parsing KOM Excel files"""
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from openpyxl import load_workbook


def parse_kom_excel(file_path):
    """
    Parse KOM Excel file and return dictionary of all extracted data
    Uses direct cell references based on the known CSV structure
    """
    wb = load_workbook(file_path, data_only=True)
    ws = wb.active
    
    data = {}
    
    # Helper function to get cell value safely
    def get_cell(row, col):
        try:
            val = ws.cell(row=row, column=col).value
            if val is None:
                return ''
            return str(val).strip()
        except:
            return ''
    
    # Helper function to get cell value as-is (for dates, numbers)
    def get_cell_raw(row, col):
        try:
            return ws.cell(row=row, column=col).value
        except:
            return None
    
    # Helper function to parse date
    def parse_date(val):
        if not val:
            return None
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, str):
            try:
                return datetime.strptime(val, '%m/%d/%y').date()
            except:
                try:
                    return datetime.strptime(val, '%m/%d/%Y').date()
                except:
                    return None
        return None
    
    # Helper function to parse decimal
    def parse_decimal(val):
        if val is None or val == '':
            return None
        if isinstance(val, (int, float)):
            return Decimal(str(val))
        val_str = str(val).replace('$', '').replace(',', '').strip()
        try:
            return Decimal(val_str)
        except:
            return None
    
    # Helper function to parse boolean
    def parse_bool(val):
        if not val:
            return False
        val_str = str(val).strip().upper()
        return val_str in ['YES', 'TRUE', '1', 'Y']
    
    # Helper function to parse boolean with NO=False
    def parse_bool_no(val):
        if not val:
            return False
        val_str = str(val).strip().upper()
        return val_str in ['YES', 'TRUE', '1', 'Y']
    
    # TO BE COMPLETED BY SALES - Row 2
    data['proposal_number'] = get_cell(2, 3)
    data['proposal_date'] = parse_date(get_cell_raw(2, 6))
    data['sales_rep'] = get_cell(2, 8)
    data['date_of_oc'] = parse_date(get_cell_raw(2, 11))
    
    # Row 4
    data['industry'] = get_cell(4, 3)
    data['industry_subcategory'] = get_cell(4, 5)
    discount_str = get_cell(4, 8)
    if discount_str:
        discount_str = discount_str.replace('%', '').strip()
        data['discount'] = parse_decimal(discount_str)
    else:
        data['discount'] = None
    data['po_number'] = get_cell(4, 11)
    
    # Commissions - Row 6
    comm1_percent = get_cell(6, 4)
    if comm1_percent:
        comm1_percent = comm1_percent.replace('%', '').strip()
        data['comm_1_inside_percent'] = parse_decimal(comm1_percent)
    else:
        data['comm_1_inside_percent'] = None
    data['comm_1_inside_name'] = get_cell(6, 6)
    comm_outside = get_cell(6, 10)
    data['comm_outside_amount'] = parse_decimal(comm_outside)
    
    # Row 8
    comm2_percent = get_cell(8, 4)
    if comm2_percent:
        comm2_percent = comm2_percent.replace('%', '').strip()
        data['comm_2_inside_percent'] = parse_decimal(comm2_percent)
    else:
        data['comm_2_inside_percent'] = None
    data['comm_2_inside_name'] = get_cell(8, 6)
    data['comm_outside_name'] = get_cell(8, 9)
    
    # BILL TO - Rows 12-24
    data['bill_to_name'] = get_cell(12, 2)
    data['bill_to_phone'] = get_cell(14, 2)
    data['bill_to_email'] = get_cell(16, 2)
    data['bill_to_company'] = get_cell(18, 2)
    data['bill_to_address'] = get_cell(20, 2)
    data['bill_to_city'] = get_cell(22, 3)
    data['bill_to_state'] = get_cell(24, 3)
    data['bill_to_zip'] = get_cell(24, 4)
    
    # SHIP TO - Rows 12-24
    data['ship_to_name'] = get_cell(12, 6)
    data['ship_to_phone'] = get_cell(14, 6)
    data['ship_to_email'] = get_cell(16, 6)
    data['ship_to_company'] = get_cell(18, 6)
    data['ship_to_address'] = get_cell(20, 6)
    data['ship_to_city'] = get_cell(22, 6)
    data['ship_to_state'] = get_cell(24, 6)
    data['ship_to_zip'] = get_cell(24, 9)
    
    # Tax - Row 26
    tax_exempt_str = get_cell(26, 4).upper()
    # YES means exempt (True), NO means not exempt (False)
    data['tax_exempt'] = (tax_exempt_str == 'YES') if tax_exempt_str else False
    exempt_cert_str = get_cell(26, 8)
    data['exempt_cert_in_hand'] = parse_bool(exempt_cert_str) if exempt_cert_str else False
    data['tax_action_who'] = get_cell(26, 11)
    data['tax_action_when'] = parse_date(get_cell_raw(27, 11))
    
    # Row 30
    tax_status_str = get_cell(30, 4)
    data['confirm_tax_status_noted'] = parse_bool(tax_status_str) if tax_status_str else False
    sage_str = get_cell(30, 6)
    data['customer_in_sage'] = parse_bool(sage_str) if sage_str else False
    
    # Payment Milestones - Rows 33-37
    for i in range(1, 6):
        row = 32 + i
        milestone_event = get_cell(row, 3)
        milestone_percent = get_cell_raw(row, 4)
        milestone_terms = get_cell(row, 5)
        milestone_notes = get_cell(row, 6)
        
        data[f'payment_milestone_{i}_event'] = milestone_event
        data[f'payment_milestone_{i}_percent'] = parse_decimal(milestone_percent)
        data[f'payment_milestone_{i}_terms'] = milestone_terms
        data[f'payment_milestone_{i}_notes'] = milestone_notes
    
    # Row 43
    data['consultant'] = get_cell(43, 3)
    data['contractor_name'] = get_cell(43, 6)
    
    # Row 45
    data['desired_delivery'] = get_cell(45, 3)
    
    # SHIPPING - Row 48
    data['freight'] = get_cell(48, 3)
    intl_str = get_cell(48, 6)
    data['international'] = not parse_bool_no(intl_str) if intl_str else False  # NO means False
    data['international_freight_method'] = get_cell(48, 10)
    
    # Row 50
    data['shipping_instructions'] = get_cell(50, 3)
    
    # SPECIFICATIONS - Row 53
    specs_str = get_cell(53, 4)
    data['specifications_provided'] = parse_bool(specs_str) if specs_str else False
    agreed_str = get_cell(53, 6)
    data['specifications_agreed'] = parse_bool(agreed_str) if agreed_str else False
    ld_str = get_cell(53, 10)
    data['liquidated_damages'] = parse_bool(ld_str) if ld_str else False
    data['liquidated_damages_rate_cap'] = get_cell(54, 10)
    
    # Row 55
    passivation_str = get_cell(55, 3)
    data['passivation'] = parse_bool(passivation_str) if passivation_str else False
    data['passivation_in_out_both'] = get_cell(55, 6)
    
    # APPROVAL PRINTS - Row 57
    approval_dates_str = get_cell(57, 7)
    if approval_dates_str:
        # Store the full string, then parse into separate parts
        data['approval_prints_ll_mech'] = approval_dates_str
        # Parse "LL & Mech: 10/17 ; Elect: 10/22" for separate display
        parts = approval_dates_str.split(';')
        ll_mech_part = parts[0].strip() if len(parts) > 0 else ''
        elect_part = parts[1].strip() if len(parts) > 1 else ''
        
        # Extract just the date portion for approval_prints_elect
        if 'Elect:' in elect_part:
            elect_date_str = elect_part.replace('Elect:', '').strip()
            data['approval_prints_elect'] = elect_date_str
        else:
            data['approval_prints_elect'] = ''
    else:
        data['approval_prints_ll_mech'] = ''
        data['approval_prints_elect'] = ''
    
    # Row 58
    approval_req_str = get_cell(58, 4)
    data['approval_prints_required'] = parse_bool(approval_req_str) if approval_req_str else False
    electrical_str = get_cell(58, 6)
    data['approval_prints_electrical'] = parse_bool(electrical_str) if electrical_str else False
    
    # Row 59
    eng_order_str = get_cell(59, 6)
    data['engineering_order_prior_to_approval'] = parse_bool(eng_order_str) if eng_order_str else False
    
    # EQUIPMENT - HTR - 1 (Row 61-63)
    data['htr_1_qty'] = parse_decimal(get_cell(61, 4))
    data['htr_1_type'] = get_cell(61, 6)
    data['htr_1_emissions'] = get_cell(61, 9)
    htr1_size = get_cell(63, 2)
    htr1_unit = get_cell(63, 3)
    data['htr_1_size'] = f"{htr1_size} {htr1_unit}".strip() if htr1_size else ''
    data['htr_1_pump_grav'] = get_cell(63, 6)
    data['htr_1_material'] = get_cell(63, 8)
    
    # HTR - 2 (Row 65-67)
    data['htr_2_qty'] = parse_decimal(get_cell(65, 4))
    data['htr_2_type'] = get_cell(65, 6)
    data['htr_2_emissions'] = get_cell(65, 9)
    htr2_size = get_cell(67, 2)
    htr2_unit = get_cell(67, 3)
    data['htr_2_size'] = f"{htr2_size} {htr2_unit}".strip() if htr2_size else ''
    data['htr_2_pump_grav'] = get_cell(67, 6)
    data['htr_2_material'] = get_cell(67, 8)
    
    # STK ECON (Row 69)
    data['stk_econ_size_bhp'] = get_cell(69, 3)
    data['stk_econ_pump_grav'] = get_cell(69, 6)
    data['stk_econ_material'] = get_cell(69, 8)
    
    # STACK(S) (Row 71)
    data['stack_length_ft'] = parse_decimal(get_cell(71, 4))
    data['stack_total'] = get_cell(71, 6)
    caps_str = get_cell(71, 9)
    data['stack_caps'] = parse_bool(caps_str) if caps_str else False
    
    # HR (Row 73)
    data['hr_sections'] = parse_decimal(get_cell(73, 3))
    data['hr_diam_in'] = parse_decimal(get_cell(73, 5))
    data['hr_tubes'] = get_cell(73, 7)
    data['hr_material'] = get_cell(73, 9)
    
    # TANKS (Rows 77-81)
    for i in range(1, 4):
        row = 76 + (i * 2)
        data[f'tank_{i}_type'] = get_cell(row, 3)
        data[f'tank_{i}_dia_in'] = parse_decimal(get_cell(row, 5))
        data[f'tank_{i}_ht_ft'] = parse_decimal(get_cell(row, 7))
        data[f'tank_{i}_ga'] = get_cell(row, 9)
        data[f'tank_{i}_material'] = get_cell(row, 11)
    
    # PUMPS (Row 83, 85-91)
    data['pump_packaging'] = get_cell(83, 3)
    data['pump_piping_material'] = get_cell(83, 6)
    
    for i in range(1, 5):
        row = 84 + (i * 2)
        data[f'pump_{i}_type'] = get_cell(row, 3)
        data[f'pump_{i}_qty'] = parse_decimal(get_cell(row, 5))
        data[f'pump_{i}_flow_gpm'] = parse_decimal(get_cell(row, 7))
        data[f'pump_{i}_tdh_ft'] = parse_decimal(get_cell(row, 9))
    
    # Steam Heaters (Rows 94-96)
    for i in range(1, 3):
        row = 93 + (i * 2)
        # Look for "Dia(in) x L(in)" pattern - might be in column 4
        dia_val = get_cell(row, 4)
        if 'x' in dia_val:
            parts = dia_val.split('x')
            if len(parts) >= 2:
                data[f'steam_heater_{i}_dia_in'] = parse_decimal(parts[0].strip())
                data[f'steam_heater_{i}_length_in'] = parse_decimal(parts[1].strip())
        else:
            data[f'steam_heater_{i}_dia_in'] = None
            data[f'steam_heater_{i}_length_in'] = None
        data[f'steam_heater_{i}_material'] = get_cell(row, 6)
        data[f'steam_heater_{i}_valve_type'] = get_cell(row, 9)
    
    # SOFTENER (Row 99)
    asme_str = get_cell(99, 3)
    data['softener_asme_coded'] = parse_bool(asme_str) if asme_str else False
    data['softener_tank_material'] = get_cell(99, 6)
    data['softener_face_plumbing_material'] = get_cell(99, 9)
    
    # PANEL(S) (Row 102)
    data['panel_qty'] = parse_decimal(get_cell(102, 3))
    data['panel_plc'] = get_cell(102, 6)
    data['panel_split_volt'] = get_cell(102, 9)
    
    # OTHER (Row 105)
    vent_str = get_cell(105, 2)
    data['other_vent_condenser'] = 'Vent Condenser' in vent_str or bool(vent_str)
    shaker_str = get_cell(105, 4)
    data['other_shaker_screen'] = 'Shaker Screen' in shaker_str or bool(shaker_str)
    
    # UTILITIES (Rows 107-113)
    data['city_water_meter_in'] = parse_decimal(get_cell(107, 8))
    data['electrical'] = get_cell(109, 3)
    data['fuel_type'] = get_cell(109, 6)
    gas_pressure = get_cell(109, 9)
    gas_pressure_unit = get_cell(109, 10)
    data['gas_pressure_psi'] = f"{gas_pressure} {gas_pressure_unit}".strip() if gas_pressure else ''
    data['onsite_gas_supply_diameter_in'] = parse_decimal(get_cell(111, 5))
    data['gas_train_orientation'] = get_cell(111, 9)
    match_str = get_cell(113, 8)
    data['utilities_match_proposal'] = parse_bool(match_str) if match_str else False
    
    # OTHER INFO (Rows 116-118)
    notes = get_cell(116, 3)
    other_info = get_cell(118, 2)
    data['notes'] = f"{notes}\n{other_info}".strip() if other_info else notes
    
    # Project Info (Row 123)
    data['project_name'] = get_cell(123, 4)
    data['project_type'] = get_cell(123, 8)
    
    # TO BE COMPLETED BY APPS - Line Items (Rows 127-139)
    line_items = []
    for row in range(127, 140):
        item_num = get_cell(row, 1)
        description = get_cell(row, 3)
        val1 = get_cell_raw(row, 6)
        val2 = get_cell_raw(row, 7)
        val3 = get_cell_raw(row, 8)
        val4 = get_cell_raw(row, 9)
        
        if item_num or description:
            line_items.append({
                'item_number': item_num,
                'description': description,
                'value_1': parse_decimal(val1),
                'value_2': parse_decimal(val2),
                'value_3': parse_decimal(val3),
                'value_4': parse_decimal(val4),
            })
    data['line_items'] = line_items
    
    # LABOR HOURS (Row 142-145)
    hr_labor = get_cell(142, 3)
    data['labor_hr'] = hr_labor if hr_labor else '-'
    data['labor_pkg'] = parse_decimal(get_cell_raw(143, 3))
    data['labor_fab'] = parse_decimal(get_cell_raw(144, 3))
    data['labor_wiring'] = parse_decimal(get_cell_raw(145, 3))
    
    # EQUIPMENT REQUIRED (Rows 143-145)
    equipment_required = []
    # Burner (Row 143)
    burner_qty = get_cell_raw(143, 6)
    burner_kn = get_cell(143, 7)
    burner_desc = get_cell(143, 8)
    if burner_qty or burner_kn or burner_desc:
        equipment_required.append({
            'equipment_type': 'Burner',
            'qty': int(burner_qty) if burner_qty else None,
            'kn_number': burner_kn,
            'description': burner_desc,
        })
    
    # Blower (Row 144)
    blower_qty = get_cell_raw(144, 6)
    blower_kn = get_cell(144, 7)
    blower_desc = get_cell(144, 8)
    if blower_qty or blower_kn or blower_desc:
        equipment_required.append({
            'equipment_type': 'Blower',
            'qty': int(blower_qty) if blower_qty else None,
            'kn_number': blower_kn,
            'description': blower_desc,
        })
    
    # Media (Row 145)
    media_qty = get_cell_raw(145, 6)
    media_kn = get_cell(145, 7)
    media_desc = get_cell(145, 8)
    if media_qty or media_kn or media_desc:
        equipment_required.append({
            'equipment_type': 'Media',
            'qty': int(media_qty) if media_qty else None,
            'kn_number': media_kn,
            'description': media_desc,
        })
    
    data['equipment_required'] = equipment_required
    
    # CAPITAL (Rows 149-157)
    capital_sell = get_cell(149, 3)
    data['capital_sell_price'] = parse_decimal(capital_sell)
    capital_equip = get_cell(151, 3)
    data['capital_equip_cost'] = parse_decimal(capital_equip)
    capital_freight = get_cell(153, 3)
    data['capital_freight'] = parse_decimal(capital_freight)
    startup = get_cell(155, 4)
    data['capital_startup_cost'] = parse_decimal(startup)
    protect = get_cell(156, 3)
    data['capital_protect_cost'] = parse_decimal(protect)
    net_rev = get_cell(157, 3)
    data['capital_net_revenue'] = parse_decimal(net_rev)
    
    # INSTALL (Rows 149-157, different columns)
    install_sell = get_cell(149, 8)
    data['install_sell_price'] = parse_decimal(install_sell)
    install_cost = get_cell(151, 8)
    data['install_cost'] = parse_decimal(install_cost)
    install_trips = get_cell(154, 8)
    data['install_trips'] = int(install_trips) if install_trips and install_trips.isdigit() else None
    install_days = get_cell(155, 8)
    data['install_days'] = int(install_days) if install_days and install_days.isdigit() else None
    install_net = get_cell(157, 8)
    data['install_net_revenue'] = parse_decimal(install_net)
    
    # TO BE COMPLETED BY ENG (Rows 161-165)
    weld_str = get_cell(161, 3)
    data['eng_weld_in_out'] = parse_bool(weld_str) if weld_str else False
    height_str = get_cell(161, 6)
    data['eng_height_greater_than_20ft'] = parse_bool(height_str) if height_str else False
    crane_str = get_cell(161, 9)
    data['eng_crane_reqd'] = parse_bool(crane_str) if crane_str else False
    
    hi_temp_str = get_cell(163, 3)
    data['eng_hi_temp_htr'] = parse_bool(hi_temp_str) if hi_temp_str else False
    large_hp_str = get_cell(163, 6)
    data['eng_large_hp_or_excessive_ll_pumps'] = parse_bool(large_hp_str) if large_hp_str else False
    generator_str = get_cell(163, 9)
    data['eng_generator_need'] = parse_bool(generator_str) if generator_str else False
    
    testing_str = get_cell(165, 3)
    data['eng_special_testing_reqd'] = parse_bool(testing_str) if testing_str else False
    lift_str = get_cell(165, 6)
    data['eng_extra_forklift_or_scissor_lift_reqd'] = parse_bool(lift_str) if lift_str else False
    
    return data
