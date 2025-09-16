from django.db import models
from django.conf import settings

class Stakeholder(models.Model):
    """Represents an owner of securities (e.g., a founder, investor)."""
    class StakeholderType(models.TextChoices):
        FOUNDER = 'FOUNDER', 'Founder'
        INVESTOR = 'INVESTOR', 'Investor'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    company_code = models.CharField(max_length=12, db_index=True)
    name = models.CharField(max_length=255)
    stakeholder_type = models.CharField(max_length=50, choices=StakeholderType.choices)

    def __str__(self):
        return f"{self.name} ({self.company_code})"

class Security(models.Model):
    """Represents a class of shares (e.g., Common Stock, Series A Preferred)."""
    company_code = models.CharField(max_length=12, db_index=True)
    name = models.CharField(max_length=255, help_text="e.g., Common Stock")
    authorized_shares = models.BigIntegerField()

    def __str__(self):
        return f"{self.name} ({self.company_code})"

class Issuance(models.Model):
    """A single transaction of issuing shares to a stakeholder."""
    company_code = models.CharField(max_length=12, db_index=True)
    stakeholder = models.ForeignKey(Stakeholder, on_delete=models.CASCADE, related_name='issuances')
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name='issuances')
    date_issued = models.DateField()
    number_of_shares = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.number_of_shares} shares to {self.stakeholder.name}"
