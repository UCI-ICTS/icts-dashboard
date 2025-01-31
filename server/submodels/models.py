#!/usr/bin/env python
# submodels/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _

class ReportedRace(models.Model):
    name = models.CharField(
        primary_key=True,
        max_length=100,
        unique=True
    )
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class InternalProjectId(models.Model):
    internal_project_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="An identifier used by GREGoR research centers to identify "
        "a set of participants for their internal tracking",
    )

    def __str__(self):
        return self.internal_project_id


class PmidId(models.Model):
    pmid_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Publication which included participant; Used for "
        "publications which include participant known prior to or after"
        " inclusion in GREGoR",
    )

    def __str__(self):
        return str(self.pmid_id)

    
class VariantType(models.TextChoices):
    SNVINDEL = "SNV/INDEL", "Single Nucleotide Variant or Insertion/Deletion"
    SV = "SV", "Structural Variant"
    RE = "RE", "Repeat Expansion"


class Zygosity(models.TextChoices):
    HOMOZYGOUS = "Homozygous", "Homozygous"
    HETEROZYGOUS = "Heterozygous", "Heterozygous"
    HEMIZYGOUS = "Hemizygous", "Hemizygous"
    HETEROPLASMY = "Heteroplasmy", "Heteroplasmy"
    HOMOPLASMY = "Homoplasmy", "Homoplasmy"
    MOSAIC = "Mosaic", "Mosaic"
    UNKNOWN = "Unknown", "Unknown"


class VariantInheritance(models.TextChoices):
    DE_NOVO = "de novo", "De Novo"
    MATERNAL = "maternal", "Maternal"
    PATERNAL = "paternal", "Paternal"
    BIPARENTAL = "biparental", "Biparental"
    NONMATERNAL = "nonmaternal", "Nonmaternal"
    NONPATERNAL = "nonpaternal", "Nonpaternal"
    UNKNOWN = "unknown", "Unknown"


class GeneDiseaseValidity(models.TextChoices):
    VALID = "Valid", "Valid"
    INVALID = "Invalid", "Invalid"


class DiscoveryMethod(models.TextChoices):
    SR_ES = "SR-ES", "Short Read Exome Sequencing"
    SR_GS = "SR-GS", "Short Read Genome Sequencing"
    LR_GS = "LR-GS", "Long Read Genome Sequencing"
    SNP_ARRAY = "SNP array", "SNP Array"
    OPTICAL_MAPPING = "Optical mapping", "Optical Mapping"
    KARYOTYPE = "Karyotype", "Karyotype"
    SR_RNA_SEQ = "SR RNA-seq", "Short Read RNA Sequencing"
    LR_RNA_SEQ = "LR RNA-seq", "Long Read RNA Sequencing"
    SR_ES_REANALYSIS = "SR-ES-reanalysis", "Short Read Exome Sequencing Reanalysis"
    SR_GS_REANALYSIS = "SR-GS-reanalysis", "Short Read Genome Sequencing Reanalysis"
    LR_GS_REANALYSIS = "LR-GS-reanalysis", "Long Read Genome Sequencing Reanalysis"
    SNP_ARRAY_REANALYSIS = "SNP array-reanalysis", "SNP Array Reanalysis"
    OPTICAL_MAPPING_REANALYSIS = (
        "Optical mapping-reanalysis",
        "Optical Mapping Reanalysis",
    )
    KARYOTYPE_REANALYSIS = "Karyotype-reanalysis", "Karyotype Reanalysis"
    SR_RNA_SEQ_REANALYSIS = (
        "SR RNA-seq-reanalysis",
        "Short Read RNA Sequencing Reanalysis",
    )
    LR_RNA_SEQ_REANALYSIS = (
        "LR RNA-seq-reanalysis",
        "Long Read RNA Sequencing Reanalysis",
    )


class GregorCenter(models.TextChoices):
    BCM = "BCM", _("Baylor College of Medicine Research Center")
    BROAD = "BROAD", _("Broad Institute")
    CNH_I = "CNH_I", _("Children's National Hospital")
    UCI = "UCI", _("University of California Irvine")
    UW_CRDR = "UW_CRDR", _("University of Washington Center for Rare Disease Research")
    GSS = "GSS", _("GREGoR Stanford Site")
    UW_DCC = "UW_DCC", _("University of Washington’s School of Public Health")


class ConsentCode(models.TextChoices):
    GRU = "GRU", _("GRU")
    HMB = "HMB", _("HMB")


class YesNo(models.TextChoices):
    YES = "Yes", _("Yes")
    NO = "No", _("No")


class Consanguinity(models.TextChoices):
    NONE_SUSPECTED = "None suspected", _("None suspected")
    SUSPECTED = "Suspected", _("Suspected")
    PRESENT = "Present", _("Present")
    UNKNOWN = "Unknown", _("Unknown")


class TwinId(models.Model):
    twin_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="may be monozygotic, dizygotic, or polyzygotic",
    )

    def __str__(self):
        return self.twin_id
    

class ProbandRelationship(models.TextChoices):
    SELF = "Self", _("SELF")
    MOTHER = "Mother", _("MOTHER")
    FATHER = "Father", _("FATHER")
    SIBLING = "Sibling", _("SIBLING")
    CHILD = "Child", _("CHILD")
    MATERNAL_HALF_SIBLING = "Maternal Half Sibling", _("MATERNAL_HALF_SIBLING")
    PATERNAL_HALF_SIBLING = "Paternal Half Sibling", _("PATERNAL_HALF_SIBLING")
    MATERNAL_GRANDMOTHER = "Maternal Grandmother", _("MATERNAL_GRANDMOTHER")
    MATERNAL_GRANDFATHER = "Maternal Grandfather", _("MATERNAL_GRANDFATHER")
    PATERNAL_GRANDMOTHER = "Paternal Grandmother", _("PATERNAL_GRANDMOTHER")
    PATERNAL_GRANDFATHER = "Paternal Grandfather", _("PATERNAL_GRANDFATHER")
    MATERNAL_AUNT = "Maternal Aunt", _("MATERNAL_AUNT")
    MATERNAL_UNCLE = "Maternal Uncle", _("MATERNAL_UNCLE")
    PATERNAL_AUNT = "Paternal Aunt", _("PATERNAL_AUNT")
    PATERNAL_UNCLE = "Paternal Uncle", _("PATERNAL_UNCLE")
    NIECE = "Niece", _("NIECE")
    NEPHEW = "Nephew", _("NEPHEW")
    MATERNAL_FIRST_COUSIN = "Maternal 1st Cousin", _("MATERNAL_FIRST_COUSIN")
    PATERNAL_FIRST_COUSIN = "Paternal 1st Cousin", _("PATERNAL_FIRST_COUSIN")
    OTHER = "Other", _("OTHER")
    UNKNOWN = "Unknown", _("UNKNOWN")
    
class BiologicalSex(models.TextChoices):
    FEMALE = "Female", _("FEMALE")
    MALE = "Male", _("MALE")
    UNKNOWN = "Unknown", _("UNKNOWN")


class ReportedEthnicity(models.TextChoices):
    HISPANIC = "Hispanic or Latino", _(
        "HISPANIC",
    )
    NON_HISPANIC = "Not Hispanic or Latino", _("NON_HISPANIC")
