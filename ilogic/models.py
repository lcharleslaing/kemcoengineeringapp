from django.db import models
from django.contrib.auth.models import User
import json


class Assembly(models.Model):
    """Top-level assembly (e.g., "Heater Assembly", "Tank Assembly")"""
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    inventor_file_path = models.CharField(max_length=500, blank=True, help_text="Path to Inventor assembly file")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Assemblies"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Component(models.Model):
    """Component within an assembly (e.g., "RFSO FLANGE 150LB:1", "PIPE SS304 S-5 22.5 DEG.:1")"""
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=255, db_index=True, help_text="Component name as it appears in Inventor")
    inventor_instance_name = models.CharField(max_length=255, blank=True, help_text="Instance name in Inventor (e.g., ':1')")
    component_type = models.CharField(max_length=100, blank=True, help_text="Type: Flange, Pipe, Tank, etc.")
    description = models.TextField(blank=True)
    parent_component = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_components', help_text="Parent component in hierarchy")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['assembly', 'name']
        unique_together = [['assembly', 'name']]
    
    def __str__(self):
        return f"{self.assembly.name} > {self.name}"


class Rule(models.Model):
    """iLogic rule attached to a component"""
    RULE_TYPE_CHOICES = [
        ('parameter', 'Parameter'),
        ('iproperty', 'iProperty'),
        ('part_number', 'Part Number'),
        ('description', 'Description'),
        ('mixed', 'Mixed'),
        ('other', 'Other'),
    ]
    
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='rules')
    rule_name = models.CharField(max_length=255, help_text="Name of the rule in Inventor")
    rule_code = models.TextField(help_text="Full iLogic VBA code")
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES, default='mixed')
    triggers = models.JSONField(default=list, blank=True, help_text="List of parameters that trigger this rule (e.g., ['FlangeSize', 'MATERIAL'])")
    dependencies = models.JSONField(default=list, blank=True, help_text="List of other rules/components this depends on")
    extracted_data = models.JSONField(default=dict, blank=True, help_text="Extracted data: part numbers, parameters, etc.")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['component', 'rule_name']
        unique_together = [['component', 'rule_name']]
    
    def __str__(self):
        return f"{self.component} > {self.rule_name}"


class RuleVersion(models.Model):
    """Version history for rules"""
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    code_snapshot = models.TextField()
    change_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rule', '-version_number']
        unique_together = [['rule', 'version_number']]
    
    def __str__(self):
        return f"{self.rule} v{self.version_number}"


class Inconsistency(models.Model):
    """Logged inconsistencies/errors found in rules"""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('fixed', 'Fixed'),
        ('ignored', 'Ignored'),
    ]
    
    INCONSISTENCY_TYPE_CHOICES = [
        ('description_mismatch', 'Description Mismatch (e.g., SS316 says SS304)'),
        ('missing_part_number', 'Missing Part Number (XXX placeholder)'),
        ('duplicate_part_number', 'Duplicate Part Number'),
        ('logic_inconsistency', 'Logic Inconsistency'),
        ('missing_condition', 'Missing Condition'),
        ('parameter_mismatch', 'Parameter Mismatch'),
        ('other', 'Other'),
    ]
    
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='inconsistencies', null=True, blank=True)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='inconsistencies', null=True, blank=True)
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='inconsistencies', null=True, blank=True)
    inconsistency_type = models.CharField(max_length=50, choices=INCONSISTENCY_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField(help_text="Description of the inconsistency")
    affected_components = models.JSONField(default=list, blank=True, help_text="List of affected component names")
    suggested_fix = models.TextField(blank=True, help_text="Suggested fix for this issue")
    code_location = models.CharField(max_length=500, blank=True, help_text="Location in code (line numbers, etc.)")
    found_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    found_at = models.DateTimeField(auto_now_add=True)
    fixed_at = models.DateTimeField(null=True, blank=True)
    fixed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='fixed_inconsistencies')
    
    class Meta:
        verbose_name_plural = "Inconsistencies"
        ordering = ['-severity', '-found_at']
    
    def __str__(self):
        return f"{self.get_severity_display()}: {self.get_inconsistency_type_display()} - {self.description[:50]}"


class Configurator(models.Model):
    """Configurator for simulating rule execution"""
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, related_name='configurators')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    input_parameters = models.JSONField(default=dict, blank=True, help_text="Default input parameters")
    output_bom = models.JSONField(default=dict, blank=True, help_text="Generated BOM structure")
    simulation_results = models.JSONField(default=dict, blank=True, help_text="Last simulation results")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['assembly', 'name']
    
    def __str__(self):
        return f"{self.assembly.name} - {self.name}"
