from django.db import models
from django.contrib.auth.models import User


class KOMForm(models.Model):
    """Main KOM (Kick Off Meeting) form - captures everything from the CSV"""
    
    # TO BE COMPLETED BY SALES
    proposal_number = models.CharField(max_length=50, blank=True)
    proposal_date = models.DateField(null=True, blank=True)
    sales_rep = models.CharField(max_length=100, blank=True)
    date_of_oc = models.DateField(null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    industry_subcategory = models.CharField(max_length=100, blank=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    po_number = models.CharField(max_length=100, blank=True)
    
    # Commissions
    comm_1_inside_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comm_1_inside_name = models.CharField(max_length=100, blank=True)
    comm_2_inside_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comm_2_inside_name = models.CharField(max_length=100, blank=True)
    comm_outside_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    comm_outside_name = models.CharField(max_length=100, blank=True)
    
    # BILL TO
    bill_to_name = models.CharField(max_length=100, blank=True)
    bill_to_phone = models.CharField(max_length=20, blank=True)
    bill_to_email = models.EmailField(blank=True)
    bill_to_company = models.CharField(max_length=200, blank=True)
    bill_to_address = models.CharField(max_length=200, blank=True)
    bill_to_city = models.CharField(max_length=100, blank=True)
    bill_to_state = models.CharField(max_length=2, blank=True)
    bill_to_zip = models.CharField(max_length=10, blank=True)
    
    # SHIP TO
    ship_to_name = models.CharField(max_length=100, blank=True)
    ship_to_phone = models.CharField(max_length=20, blank=True)
    ship_to_email = models.EmailField(blank=True)
    ship_to_company = models.CharField(max_length=200, blank=True)
    ship_to_address = models.CharField(max_length=200, blank=True)
    ship_to_city = models.CharField(max_length=100, blank=True)
    ship_to_state = models.CharField(max_length=2, blank=True)
    ship_to_zip = models.CharField(max_length=10, blank=True)
    
    # Tax Information
    tax_exempt = models.BooleanField(default=False)
    exempt_cert_in_hand = models.BooleanField(default=False)
    tax_action_who = models.CharField(max_length=100, blank=True)
    tax_action_when = models.DateField(null=True, blank=True)
    confirm_tax_status_noted = models.BooleanField(default=False)
    customer_in_sage = models.BooleanField(default=False)
    
    # Payment Milestones
    payment_milestone_1_event = models.CharField(max_length=100, blank=True)
    payment_milestone_1_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    payment_milestone_1_terms = models.CharField(max_length=100, blank=True)
    payment_milestone_1_notes = models.TextField(blank=True)
    
    payment_milestone_2_event = models.CharField(max_length=100, blank=True)
    payment_milestone_2_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    payment_milestone_2_terms = models.CharField(max_length=100, blank=True)
    payment_milestone_2_notes = models.TextField(blank=True)
    
    payment_milestone_3_event = models.CharField(max_length=100, blank=True)
    payment_milestone_3_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    payment_milestone_3_terms = models.CharField(max_length=100, blank=True)
    payment_milestone_3_notes = models.TextField(blank=True)
    
    payment_milestone_4_event = models.CharField(max_length=100, blank=True)
    payment_milestone_4_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    payment_milestone_4_terms = models.CharField(max_length=100, blank=True)
    payment_milestone_4_notes = models.TextField(blank=True)
    
    payment_milestone_5_event = models.CharField(max_length=100, blank=True)
    payment_milestone_5_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    payment_milestone_5_terms = models.CharField(max_length=100, blank=True)
    payment_milestone_5_notes = models.TextField(blank=True)
    
    # TO BE COMPLETED BY SALES (continued)
    consultant = models.CharField(max_length=100, blank=True)
    contractor_name = models.CharField(max_length=100, blank=True)
    desired_delivery = models.CharField(max_length=100, blank=True)
    
    # SHIPPING
    freight = models.CharField(max_length=50, blank=True)
    international = models.BooleanField(default=False)
    international_freight_method = models.CharField(max_length=100, blank=True)
    shipping_instructions = models.TextField(blank=True)
    
    # SPECIFICATIONS AND TERMS & CONDITIONS
    specifications_provided = models.BooleanField(default=False)
    specifications_agreed = models.BooleanField(default=False)
    liquidated_damages = models.BooleanField(default=False)
    liquidated_damages_rate_cap = models.CharField(max_length=200, blank=True)
    passivation = models.BooleanField(default=False)
    passivation_in_out_both = models.CharField(max_length=50, blank=True)
    
    # APPROVAL PRINTS
    approval_prints_required = models.BooleanField(default=False)
    approval_prints_electrical = models.BooleanField(default=False)
    approval_prints_ll_mech = models.CharField(max_length=200, blank=True)
    approval_prints_elect = models.CharField(max_length=200, blank=True)
    engineering_order_prior_to_approval = models.BooleanField(default=False)
    
    # EQUIPMENT - Heaters
    htr_1_qty = models.IntegerField(null=True, blank=True)
    htr_1_type = models.CharField(max_length=100, blank=True)
    htr_1_emissions = models.CharField(max_length=100, blank=True)
    htr_1_size = models.CharField(max_length=50, blank=True)
    htr_1_pump_grav = models.CharField(max_length=50, blank=True)
    htr_1_material = models.CharField(max_length=50, blank=True)
    
    htr_2_qty = models.IntegerField(null=True, blank=True)
    htr_2_type = models.CharField(max_length=100, blank=True)
    htr_2_emissions = models.CharField(max_length=100, blank=True)
    htr_2_size = models.CharField(max_length=50, blank=True)
    htr_2_pump_grav = models.CharField(max_length=50, blank=True)
    htr_2_material = models.CharField(max_length=50, blank=True)
    
    # Stack Economizer
    stk_econ_size_bhp = models.CharField(max_length=50, blank=True)
    stk_econ_pump_grav = models.CharField(max_length=50, blank=True)
    stk_econ_material = models.CharField(max_length=50, blank=True)
    
    # Stack(s)
    stack_length_ft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stack_total = models.CharField(max_length=50, blank=True)
    stack_caps = models.BooleanField(default=False)
    
    # HR
    hr_sections = models.IntegerField(null=True, blank=True)
    hr_diam_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hr_tubes = models.CharField(max_length=50, blank=True)
    hr_material = models.CharField(max_length=50, blank=True)
    
    # TANKS
    tank_1_type = models.CharField(max_length=50, blank=True)
    tank_1_dia_in = models.IntegerField(null=True, blank=True)
    tank_1_ht_ft = models.IntegerField(null=True, blank=True)
    tank_1_ga = models.CharField(max_length=50, blank=True)
    tank_1_material = models.CharField(max_length=50, blank=True)
    
    tank_2_type = models.CharField(max_length=50, blank=True)
    tank_2_dia_in = models.IntegerField(null=True, blank=True)
    tank_2_ht_ft = models.IntegerField(null=True, blank=True)
    tank_2_ga = models.CharField(max_length=50, blank=True)
    tank_2_material = models.CharField(max_length=50, blank=True)
    
    tank_3_type = models.CharField(max_length=50, blank=True)
    tank_3_dia_in = models.IntegerField(null=True, blank=True)
    tank_3_ht_ft = models.IntegerField(null=True, blank=True)
    tank_3_ga = models.CharField(max_length=50, blank=True)
    tank_3_material = models.CharField(max_length=50, blank=True)
    
    # PUMPS
    pump_packaging = models.CharField(max_length=50, blank=True)
    pump_piping_material = models.CharField(max_length=50, blank=True)
    
    pump_1_type = models.CharField(max_length=50, blank=True)
    pump_1_qty = models.IntegerField(null=True, blank=True)
    pump_1_flow_gpm = models.IntegerField(null=True, blank=True)
    pump_1_tdh_ft = models.IntegerField(null=True, blank=True)
    
    pump_2_type = models.CharField(max_length=50, blank=True)
    pump_2_qty = models.IntegerField(null=True, blank=True)
    pump_2_flow_gpm = models.IntegerField(null=True, blank=True)
    pump_2_tdh_ft = models.IntegerField(null=True, blank=True)
    
    pump_3_type = models.CharField(max_length=50, blank=True)
    pump_3_qty = models.IntegerField(null=True, blank=True)
    pump_3_flow_gpm = models.IntegerField(null=True, blank=True)
    pump_3_tdh_ft = models.IntegerField(null=True, blank=True)
    
    pump_4_type = models.CharField(max_length=50, blank=True)
    pump_4_qty = models.IntegerField(null=True, blank=True)
    pump_4_flow_gpm = models.IntegerField(null=True, blank=True)
    pump_4_tdh_ft = models.IntegerField(null=True, blank=True)
    
    # Steam Heaters
    steam_heater_1_dia_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    steam_heater_1_length_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    steam_heater_1_material = models.CharField(max_length=50, blank=True)
    steam_heater_1_valve_type = models.CharField(max_length=50, blank=True)
    
    steam_heater_2_dia_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    steam_heater_2_length_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    steam_heater_2_material = models.CharField(max_length=50, blank=True)
    steam_heater_2_valve_type = models.CharField(max_length=50, blank=True)
    
    # Softener
    softener_asme_coded = models.BooleanField(default=False)
    softener_tank_material = models.CharField(max_length=50, blank=True)
    softener_face_plumbing_material = models.CharField(max_length=50, blank=True)
    
    # Panel(s)
    panel_qty = models.IntegerField(null=True, blank=True)
    panel_plc = models.CharField(max_length=100, blank=True)
    panel_split_volt = models.CharField(max_length=50, blank=True)
    
    # Other Equipment
    other_vent_condenser = models.BooleanField(default=False)
    other_shaker_screen = models.BooleanField(default=False)
    
    # UTILITIES
    city_water_meter_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    electrical = models.CharField(max_length=50, blank=True)
    fuel_type = models.CharField(max_length=50, blank=True)
    gas_pressure_psi = models.CharField(max_length=50, blank=True)
    onsite_gas_supply_diameter_in = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gas_train_orientation = models.CharField(max_length=50, blank=True)
    utilities_match_proposal = models.BooleanField(default=False)
    
    # OTHER INFO
    notes = models.TextField(blank=True)
    other_info = models.TextField(blank=True)
    
    # Project Info
    project_name = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(max_length=50, blank=True)
    
    # TO BE COMPLETED BY APPS - Line Items
    # Will use a separate model for line items
    
    # LABOR HOURS
    labor_hr = models.CharField(max_length=50, blank=True)
    labor_pkg = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    labor_fab = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    labor_wiring = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    
    # EQUIPMENT REQUIRED
    # Will use a separate model for equipment required
    
    # CAPITAL
    capital_sell_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    capital_equip_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    capital_freight = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    capital_startup_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    capital_protect_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    capital_net_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # INSTALL
    install_sell_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    install_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    install_trips = models.IntegerField(null=True, blank=True)
    install_days = models.IntegerField(null=True, blank=True)
    install_net_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # TO BE COMPLETED BY ENG
    eng_weld_in_out = models.BooleanField(default=False)
    eng_height_greater_than_20ft = models.BooleanField(default=False)
    eng_crane_reqd = models.BooleanField(default=False)
    eng_hi_temp_htr = models.BooleanField(default=False)
    eng_large_hp_or_excessive_ll_pumps = models.BooleanField(default=False)
    eng_generator_need = models.BooleanField(default=False)
    eng_special_testing_reqd = models.BooleanField(default=False)
    eng_extra_forklift_or_scissor_lift_reqd = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    source_file = models.CharField(max_length=255, blank=True)  # Original filename
    
    class Meta:
        verbose_name = "KOM Form"
        verbose_name_plural = "KOM Forms"
        ordering = ['-proposal_date', '-created_at']
    
    def __str__(self):
        return f"KOM {self.proposal_number} - {self.project_name or 'No Project Name'}"


class KOMLineItem(models.Model):
    """Line items from TO BE COMPLETED BY APPS section"""
    kom_form = models.ForeignKey(KOMForm, on_delete=models.CASCADE, related_name='line_items')
    item_number = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=500, blank=True)
    value_1 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    value_2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    value_3 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    value_4 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = "KOM Line Item"
        verbose_name_plural = "KOM Line Items"
        ordering = ['item_number']
    
    def __str__(self):
        return f"{self.item_number} - {self.description}"


class KOMEquipmentRequired(models.Model):
    """Equipment required from LABOR HOURS section"""
    kom_form = models.ForeignKey(KOMForm, on_delete=models.CASCADE, related_name='equipment_required')
    equipment_type = models.CharField(max_length=50, blank=True)  # Burner, Blower, Media, etc.
    qty = models.IntegerField(null=True, blank=True)
    kn_number = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=500, blank=True)
    
    class Meta:
        verbose_name = "KOM Equipment Required"
        verbose_name_plural = "KOM Equipment Required"
    
    def __str__(self):
        return f"{self.equipment_type} - {self.description}"
