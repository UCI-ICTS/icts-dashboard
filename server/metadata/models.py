# us
# gregordb/metadata.py

"""
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class InternalProjectId(models.Model):
    internal_project_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="An identifier used by GREGoR research centers to identify "
        "a set of participants for their internal tracking",
    )

    def __str__(self):
        return self.internal_project_id


class GregorCenter(models.TextChoices):
    BCM = "BCM", _("Baylor College of Medicine Research Center")
    BROAD = "BROAD", _("Broad Institute")
    CNHI = "CNH_I", _("Children's National Hospital")
    UWCRDR = "UW_CRDR", _("University of Washington Center for Rare Disease Research")
    GSS = "GSS", _("GREGoR Stanford Site")
    UWDCC = "UW_DCC", _("University of Washington’s School of Public Health")


class ConsentCode(models.TextChoices):
    GRU = "GRU", _("GRU")
    HMB = "HMB", _("HMB")


class Recontactable(models.TextChoices):
    YES = "Yes", _("Yes")
    NO = "No", _("No")


class Consanguinity(models.TextChoices):
    PRESENT = "Present", _("Present")
    SUSPECTED = "Suspected", _("Suspected")
    ABSENT = "Absent", _("Absent")
    UNKNOWN = "Unknown", _("Unknown")


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


class Family(models.Model):
    family_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for family (primary key). Needs to be Unique across centers, use participant.gregor_center as ID prefix.",
    )
    consanguinity = models.CharField(
        max_length=50,
        choices=Consanguinity.choices,
        default=Consanguinity.UNKNOWN,
        help_text="Indicate if consanguinity is present or suspected within a family",
    )
    consanguinity_detail = models.TextField(
        blank=True,
        help_text="Free text description of any additional consanguinity details",
    )
    pedigree_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of file (renamed from pedigree_image because it can contain a PED file or image)",
    )
    pedigree_file_detail = models.TextField(
        blank=True,
        help_text="Free text description of other family structure/pedigree file caption or legend.",
    )
    family_history_detail = models.TextField(
        blank=True,
        help_text="Details about family history that do not fit into structured fields. Family relationship terms should be relative to the proband.",
    )


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


class ReportedRace(models.TextChoices):
    NATIVE_AMERICAN = "American Indian or Alaska Native", _("NATIVE_AMERICAN")
    ASIAN = "Asian", _("ASIAN")
    BLACK = "Black or African American", _("BLACK")
    PACIFIC_ISLANDER = "Native Hawaiian or Other Pacific Islander", _(
        "PACIFIC_ISLANDER"
    )
    MIDDLE_EASTERN = "Middle Eastern or North African", _("MIDDLE_EASTERN")
    WHITE = "White", _("WHITE")


class ReportedEthnicity(models.TextChoices):
    HISPANIC = "Hispanic or Latino", _(
        "HISPANIC",
    )
    NON_HISPANIC = "Not Hispanic or Latino", _("NON_HISPANIC")


class PhenotypeDescription(models.Model):
    phenotype_description = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="For unaffected/relatives, can note 'parent of ...' or 'relative of ...'",
    )


class Participant(models.Model):
    participant_id = models.CharField(
        unique=True,
        primary_key=True,
        max_length=255,
        help_text="Subject/Participant Identifier (primary key)",
    )
    internal_project_ids = models.ManyToManyField(
        InternalProjectId,
        related_name="participants",
        blank=True,
        help_text="An identifier used by GREGoR research centers to identify"
        "a set of participants for their internal tracking",
    )
    gregor_center = models.CharField(
        max_length=255,
        blank=True,
        choices=GregorCenter.choices,
        default=None,
        help_text="GREGoR Center to which the participant is originally " "associated",
    )
    consent_code = models.CharField(
        max_length=255,
        choices=ConsentCode.choices,
        help_text="Consent group pertaining to this participant's data",
    )
    recontactable = models.CharField(
        max_length=255,
        blank=True,
        choices=Recontactable.choices,
        default="No",
        help_text="Is the originating GREGoR Center likely able to recontact "
        "this participant",
    )
    prior_testing = models.TextField(
        blank=True,
        help_text="Text description of any genetic testing for individual "
        "conducted prior to enrollment",
    )
    pmid_ids = models.ManyToManyField(
        "PmidId",
        related_name="participants",
        blank=True,
        help_text="Case specific PubMed ID if applicable",
    )
    family_id = models.ForeignKey(
        Family,
        to_field="family_id",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Identifier for family",
    )
    paternal_id = models.CharField(
        max_length=255,
        default="0",
        help_text="participant_id for father; 0 if not available",
    )
    maternal_id = models.CharField(
        max_length=255,
        default="0",
        help_text="participant_id for mother; 0 if not available",
    )
    twin_ids = models.ManyToManyField(
        TwinId,
        related_name="participants",
        blank=True,
        help_text="participant_id for twins, triplets, etc; 0 if not available",
    )
    proband_relationship = models.CharField(
        max_length=255,
        choices=ProbandRelationship.choices,
        default=ProbandRelationship.UNKNOWN,
        help_text="Text description of individual relationship to proband in family, especially useful to capture relationships when connecting distant relatives and connecting relatives not studied",
    )
    proband_relationship_detail = models.TextField(
        blank=True,
        help_text="Other proband relationship not captured in enumeration above",
    )
    sex = models.CharField(
        max_length=255,
        choices=BiologicalSex.choices,
        default=BiologicalSex.UNKNOWN,
        help_text="Biological sex assigned at birth (aligned with All of Us). If individual has a known DSD / not expected sex chromosome karyotype, this can be noted in the phenotype information section.",
    )
    sex_detail = models.TextField(
        blank=True,
        help_text="Optional free-text field to describe known discrepancies between 'sex' value (female=>XX, male=>XY) and actual sex chromosome karyotype",
    )
    reported_race = models.CharField(
        max_length=255,
        blank=True,
        help_text="Self/submitter-reported race (OMB categories",
    )
    reported_ethnicity = models.CharField(
        max_length=255,
        blank=True,
        default=None,
        choices=ReportedEthnicity.choices,
        help_text="Self/submitter-reported ethnicity (OMB categories)",
    )
    ancestry_detail = models.CharField(
        max_length=255,
        blank=True,
        help_text="Additional specific ancestry description free text beyond what is captured by OMB race/ethnicity categories",
    )
    age_at_last_observation = models.FloatField(
        blank=True,
        help_text="Age at last observation, aka age in years at the last time the center can vouch for the accuracy phenotype data. For conditions with later age of onset, this field lets users know if individuals marked as unaffected were younger or older than the age when the phenotype is expected to appear",
    )
    affected_status = models.TextField(
        blank=True,
        help_text="Indicate affected status of individual (overall with respect to primary phenotype in the family). Note: Affected participants must have entry in phenotype table.",
    )
    phenotype_description = models.TextField(
        blank=True,
        help_text="human-readable 'Phenotypic one-line summary' for why this individual is of interest. Could be the same as the term_details value in the Phenotype table. Strongly encourage/required for proband.",
    )
    age_at_enrollment = models.FloatField(
        blank=True, help_text="age in years at which consent was originally obtained"
    )
    solve_status = models.CharField(
        max_length=255,
        help_text="Indication of whether the submitting RC considers this case 'solved'",
    )
    missing_variant_case = models.TextField(
        blank=True,
        help_text="Indication of whether this is known to be a missing variant case, see notes for a description of the Missing Variant Project and inclusion criteria.",
    )
    missing_variant_details = models.TextField(
        blank=True,
        help_text="For missing variant cases, indicate gene(s) or region of interest and reason for inclusion in MVP",
    )

    def __str__(self):
        return str(self.participant_id)

    def get_pmid_ids(self):
        """Returns a list of primary key IDs for associated PmidIds."""
        return list(self.pmid_id.values_list("id", flat=True))


class Phenotype(models.Model):
    phenotype_id = models.CharField(
        max_length=255, primary_key=True, help_text="primary key"
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="phenotypes",
        help_text="Subject/Participant Identifier",
    )
    term_id = models.CharField(
        max_length=255, help_text="Identifier for the term within the ontology"
    )
    presence = models.CharField(
        max_length=100,
        choices=[("present", "Present"), ("absent", "Absent"), ("unknown", "Unknown")],
        default="unknown",
        help_text="Presence of the phenotype",
    )
    ontology = models.CharField(
        max_length=100,
        choices=[
            ("hpo", "Human Phenotype Ontology"),
            ("mp", "Mammalian Phenotype Ontology"),
            ("go", "Gene Ontology"),
        ],
        default="hpo",
        help_text="The ontology used for the term",
    )
    additional_details = models.TextField(
        blank=True,
        help_text="modifier of a term where the additional details are not supported/available as a term in HPO",
    )
    onset_age_range = models.CharField(
        max_length=100,
        choices=[
            ("neonatal", "Neonatal"),
            ("infantile", "Infantile"),
            ("childhood", "Childhood"),
            ("adolescence", "Adolescence"),
            ("adult", "Adult"),
            ("old_age", "Old Age"),
        ],
        default="unknown",
        help_text="Age range at the onset of the phenotype",
    )
    additional_modifiers = models.TextField(
        blank=True, help_text="Additional modifiers that further specify the phenotype"
    )
    syndromic = models.BooleanField(
        default=False,
        help_text="Indicates if the phenotype is part of a syndromic condition",
    )

    def __str__(self):
        return f"{self.participant.participant_id} - {self.term_id}"


class VariantType(models.TextChoices):
    SNV = "SNV", "Single Nucleotide Variant"
    INDEL = "INDEL", "Insertion/Deletion"
    SV = "SV", "Structural Variant"
    CNV = "CNV", "Copy Number Variant"
    RE = "RE", "Repeat Expansion"
    MEI = "MEI", "Mobile Element Insertion"
    STR = "STR", "Short Tandem Repeat"


class Zygosity(models.TextChoices):
    HOMOZYGOUS = "Homozygous", "Homozygous"
    HETEROZYGOUS = "Heterozygous", "Heterozygous"
    HEMIZYGOUS = "Hemizygous", "Hemizygous"


class VariantInheritance(models.TextChoices):
    DE_NOVO = "De Novo", "De Novo"
    INHERITED = "Inherited", "Inherited"
    UNKNOWN = "Unknown", "Unknown"


class GeneDiseaseValidity(models.TextChoices):
    VALID = "Valid", "Valid"
    INVALID = "Invalid", "Invalid"


class DiscoveryMethod(models.TextChoices):
    SEQUENCING = "Sequencing", "Sequencing"
    GWAS = "GWAS", "Genome Wide Association Study"


class GeneticFindings(models.Model):
    genetic_findings_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique ID of this variant in this participant",
    )
    participant_id = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        help_text="Subject/Participant Identifier within project",
    )
    experiment_id = models.CharField(
        max_length=255,
        help_text="The experiment table and experiment ID(s) in which discovery was identified",
    )
    variant_type = models.CharField(
        max_length=50, choices=VariantType.choices, help_text="Type of genetic variant"
    )
    sv_type = models.CharField(
        max_length=50, blank=True, help_text="Type of structural variant if applicable"
    )
    variant_reference_assembly = models.CharField(
        max_length=50, help_text="The genome build for identifying the variant position"
    )
    chrom = models.CharField(max_length=10, help_text="Chromosome of the variant")
    chrom_end = models.CharField(
        max_length=10, blank=True, help_text="End position chromosome of SV"
    )
    pos = models.IntegerField(help_text="Start position of the variant")
    pos_end = models.IntegerField(blank=True, null=True, help_text="End position of SV")
    ref = models.CharField(max_length=255, help_text="Reference allele of the variant")
    alt = models.CharField(max_length=255, help_text="Alternate allele of the variant")
    copy_number = models.IntegerField(
        blank=True, null=True, help_text="CNV copy number"
    )
    ClinGen_allele_ID = models.CharField(
        max_length=255,
        blank=True,
        help_text="ClinGen Allele ID for cross table reference",
    )
    gene_of_interest = models.CharField(
        max_length=255,
        help_text="HGNC approved symbol of the known or candidate gene(s)",
    )
    transcript = models.CharField(
        max_length=255,
        blank=True,
        help_text="Text description of transcript overlapping the variant",
    )
    hgvsc = models.CharField(
        max_length=255, blank=True, help_text="HGVS c. description of the variant"
    )
    hgvsp = models.CharField(
        max_length=255, blank=True, help_text="HGVS p. description of the variant"
    )
    hgvs = models.CharField(
        max_length=255, blank=True, help_text="Genomic HGVS description of the variant"
    )
    zygosity = models.CharField(
        max_length=50, choices=Zygosity.choices, help_text="Zygosity of variant"
    )
    allele_balance_or_heteroplasmy_percentage = models.FloatField(
        blank=True,
        null=True,
        help_text="Reported allele balance (mosaic) or heteroplasmy percentage (mitochondrial)",
    )
    variant_inheritance = models.CharField(
        max_length=50,
        choices=VariantInheritance.choices,
        help_text="Detection of variant in parents",
    )
    linked_variant = models.CharField(
        max_length=255, blank=True, help_text="Second variant in recessive cases"
    )
    linked_variant_phase = models.CharField(
        max_length=50, blank=True, help_text="Phase of linked variants"
    )
    gene_known_for_phenotype = models.CharField(
        max_length=50,
        blank=True,
        help_text="Indicate if the gene listed is a candidate or known disease gene",
    )
    known_condition_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Condition name consistent with the variant/phenotype/inheritance",
    )
    condition_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="MONDO/OMIM number for condition used for variant interpretation",
    )
    condition_inheritance = models.CharField(
        max_length=50,
        blank=True,
        help_text="Expected inheritance of the condition used for variant interpretation",
    )
    GREGoR_variant_classification = models.CharField(
        max_length=50,
        blank=True,
        help_text="Clinical significance of variant described to condition listed as determined by the RC's variant curation",
    )
    GREGoR_ClinVar_SCV = models.CharField(
        max_length=255,
        blank=True,
        help_text="ClinVar accession number for the variant curation submitted by your center",
    )
    gene_disease_validity = models.CharField(
        max_length=50,
        choices=GeneDiseaseValidity.choices,
        help_text="Validity assessment of the gene-disease relationship",
    )
    public_database_other = models.CharField(
        max_length=255,
        blank=True,
        help_text="Public databases that this variant in this participant has been submitted by the RC",
    )
    public_database_ID_other = models.CharField(
        max_length=255, blank=True, help_text="Public database variant/case ID"
    )
    phenotype_contribution = models.CharField(
        max_length=50,
        blank=True,
        help_text="Contribution of variant-linked condition to participant's phenotype",
    )
    partial_contribution_explained = models.ManyToManyField(
        Phenotype,
        blank=True,
        help_text="Specific phenotypes explained by the condition associated with this variant/gene in cases of partial contribution",
    )
    additional_family_members_with_variant = models.ManyToManyField(
        Participant,
        blank=True,
        related_name="family_variants",
        help_text="List of related participant IDs carrying the same variant",
    )
    method_of_discovery = models.CharField(
        max_length=50,
        choices=DiscoveryMethod.choices,
        help_text="The method/assay(s) used to identify the candidate",
    )
    notes = models.TextField(
        blank=True,
        help_text="Free text field to explain edge cases or discovery updates or list parallel experiment IDs or list parental allele balance when mosaic... etc.",
    )

    def __str__(self):
        return self.genetic_findings_id


class Analyte(models.Model):
    analyte_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for an analyte from a primary biosample source",
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        help_text="The participant from whom the biosample was taken",
    )
    analyte_type = models.CharField(
        max_length=50,
        choices=[
            ("DNA", "DNA"),
            ("RNA", "RNA"),
            ("cDNA", "cDNA"),
            ("blood plasma", "blood plasma"),
            ("frozen whole blood", "frozen whole blood"),
            ("high molecular weight DNA", "high molecular weight DNA"),
            ("urine", "urine"),
        ],
        help_text="Analyte derived from the primary biosample. The actual thing you're sticking into a machine to analyze/sequence",
    )
    analyte_processing_details = models.TextField(
        help_text="Details about how the analyte or original biosample was extracted or processed"
    )
    primary_biosample = models.CharField(
        max_length=100,
        choices=[
            ("UBERON:0000479", "tissue"),
            ("UBERON:0003714", "neural tissue"),
            ("UBERON:0001836", "saliva"),
            ("UBERON:0001003", "skin epidermis"),
            ("UBERON:0002385", "muscle tissue"),
            ("UBERON:0000178", "whole blood"),
            ("UBERON:0002371", "bone marrow"),
            ("UBERON:0006956", "buccal mucosa"),
            ("UBERON:0001359", "cerebrospinal fluid"),
            ("UBERON:0001088", "urine"),
            ("UBERON:0019306", "nose epithelium"),
            ("CL:0000034", "iPSC"),
            ("CL:0000576", "monocytes - PBMCs"),
            ("CL:0000542", "lymphocytes - LCLs"),
            ("CL:0000057", "fibroblasts"),
            ("UBERON:0005291", "embryonic tissue"),
            ("CL:0011020", "iPSC NPC"),
            ("UBERON:0002037", "cerebellum tissue"),
            ("UBERON:0001133", "cardiac tissue"),
        ],
        help_text="Tissue type of biosample taken from the participant that the analyte was extracted or processed from",
    )
    primary_biosample_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional ID for the biosample; allows for linking of multiple analytes extracted or processed from the same biosample",
    )
    primary_biosample_details = models.TextField(
        blank=True,
        help_text="Free text to capture information not in structured fields",
    )
    tissue_affected_status = models.BooleanField(
        default=False,
        help_text="If applicable to disease (suspected mosaic), indicates if the tissue is from an affected source.",
    )
    age_at_collection = models.FloatField(
        help_text="Age of participant in years at biosample collection"
    )
    participant_drugs_intake = models.TextField(
        help_text="The list of drugs patient is on, at the time of sample collection. Helpful during analysis of metabolomics and immune assays"
    )
    participant_special_diet = models.TextField(
        help_text="If the patient was fasting, when the sample was collected. Relevant when analyzing metabolomics data"
    )
    hours_since_last_meal = models.FloatField(
        help_text="Hours since last meal, relevant when analyzing metabolomics data"
    )
    passage_number = models.IntegerField(
        help_text="Passage number is relevant for fibroblast cultures and possibly iPSC."
    )
    time_to_freeze = models.FloatField(
        help_text="Time (in hours) from collection to freezing the sample. Delayed freeze turns out to be useful / important info for PaxGene blood (for RNA isolation)."
    )
    sample_transformation_detail = models.TextField(
        help_text="Details regarding sample transformation"
    )
    quality_issues = models.TextField(
        help_text="Freetext (limited characters) to concisely describe if there are any QC issues that would be important to note"
    )

    def __str__(self):
        return f"Analyte {self.analyte_id} from participant {self.participant.participant_id}"


class Experiment(models.Model):
    EXPERIMENT_TYPES = [
        ("experiment_dna_short_read", "DNA Short Read"),
        ("experiment_rna_short_read", "RNA Short Read"),
        ("experiment_nanopore", "Nanopore"),
        ("experiment_pac_bio", "Pac Bio"),
        ("experiment_atac_short_read", "ATAC Short Read"),
    ]

    experiment_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique ID of this experiment instance combining the table name and an ID within the table.",
    )
    table_name = models.CharField(
        max_length=50,
        choices=EXPERIMENT_TYPES,
        help_text="Specifies the experiment table.",
    )
    id_in_table = models.CharField(
        max_length=255,
        help_text="Unique identifier within the specific experiment table.",
    )
    participant = models.ForeignKey(
        "Participant",
        on_delete=models.CASCADE,
        help_text="References the participant associated with this experiment.",
    )

    def __str__(self):
        return f"{self.table_name} - {self.experiment_id}"


class Aligned(models.Model):
    aligned_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        help_text="Automatically generated as table_name.aligned_id_in_table",
    )
    table_name = models.CharField(
        max_length=50,
        choices=[
            ("aligned_dna_short_read", "Aligned DNA Short Read"),
            ("aligned_rna_short_read", "Aligned RNA Short Read"),
            ("aligned_nanopore", "Aligned Nanopore"),
            ("aligned_pac_bio", "Aligned Pac Bio"),
            ("aligned_atac_short_read", "Aligned ATAC Short Read"),
        ],
        help_text="The specific table this aligned data entry references",
    )
    id_in_table = models.CharField(
        max_length=255,
        help_text="Identifier for the specific entry in the referenced table",
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        help_text="The participant associated with this aligned data",
    )
    aligned_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Path to the file containing the aligned data",
    )
    aligned_index_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Path to the index file associated with the aligned data",
    )

    def save(self, *args, **kwargs):
        """Set the aligned_id based on table_name and id_in_table before saving"""

        self.aligned_id = f"{self.table_name}.{self.id_in_table}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.aligned_id


class ExperimentDNAShortRead(models.Model):
    experiment_dna_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="identifier for experiment_dna_short_read (primary key)",
    )
    analyte = models.ForeignKey(
        Analyte,
        on_delete=models.CASCADE,
        help_text="reference to an analyte from which this experiment was derived",
    )
    experiment_sample_id = models.CharField(
        max_length=255, help_text="identifier used in the data file"
    )
    seq_library_prep_kit_method = models.CharField(
        max_length=255, blank=True, help_text="Library prep kit used"
    )
    read_length = models.IntegerField(
        null=True, blank=True, help_text="sequenced read length (bp)"
    )
    experiment_type = models.CharField(
        max_length=50,
        choices=[("targeted", "Targeted"), ("genome", "Genome"), ("exome", "Exome")],
        help_text="type of sequencing experiment performed",
    )
    targeted_regions_method = models.CharField(
        max_length=255, blank=True, help_text="Which capture kit is used"
    )
    targeted_region_bed_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="name and path of bed file uploaded to workspace",
    )
    date_data_generation = models.DateField(
        null=True,
        blank=True,
        help_text="Date of data generation (First sequencing date)",
    )
    target_insert_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="insert size the protocol targets for DNA fragments",
    )
    sequencing_platform = models.CharField(
        max_length=100,
        blank=True,
        help_text="sequencing platform used for the experiment",
    )
    sequencing_event_details = models.TextField(
        blank=True,
        help_text="describe if there are any sequencing-specific issues that would be important to note",
    )


class AlignedDNAShortRead(models.Model):
    aligned_dna_short_read_id = models.CharField(max_length=255, primary_key=True)
    experiment_dna_short_read = models.ForeignKey(
        "ExperimentDNAShortRead", on_delete=models.CASCADE
    )
    aligned_dna_short_read_file = models.URLField(max_length=1024)
    aligned_dna_short_read_index_file = models.URLField(max_length=1024)
    md5sum = models.CharField(max_length=32, unique=True)
    reference_assembly = models.CharField(
        max_length=50,
        choices=[
            ("GRCh38", "GRCh38"),
            ("GRCh37", "GRCh37"),
            ("NCBI36", "NCBI36"),
            ("NCBI35", "NCBI35"),
            ("NCBI34", "NCBI34"),
        ],
    )
    reference_assembly_uri = models.URLField(blank=True, null=True)
    reference_assembly_details = models.TextField(blank=True, null=True)
    alignment_software = models.CharField(max_length=255)
    mean_coverage = models.FloatField(null=True, blank=True)
    analysis_details = models.TextField(blank=True, null=True)
    quality_issues = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Aligned DNA Short Read"
        verbose_name_plural = "Aligned DNA Short Reads"

    def __str__(self):
        return self.aligned_dna_short_read_id


class AlignedDNAShortReadSet(models.Model):
    aligned_dna_short_read_set_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="identifier for a set of experiments (primary key). For "
        + "centers uploading multi-sample files, they will need to come up"
        + " with a value for aligned_short_read_set_id that makes sense to"
        + " them for indicating the sample group for a multi-sample "
        + "callset, and use that same value in called_variants_short_read.",
    )
    aligned_dna_short_reads = models.ManyToManyField(
        AlignedDNAShortRead,
        help_text="the identifiers for single-sample aligned_dna_short_reads"
        + " included in the read_set",
    )

    def __str__(self):
        return self.aligned_dna_short_read_set_id

    # Conditional validation method could be implemented here if necessary.
    # (e.g., linking to called_variants_dna_short_read) would be handled in
    # the application logic layer, likely in the form of custom validations
    # within the model's save method or a Django form/serializer layer,
    # depending on how the data is being managed and accessed within your
    # application.


class CalledVariantsDNAShortRead(models.Model):
    """
    The variant_types field is simplified to a CharField but might want
    to implement it as a ManyToManyField using a separate model if
    application requires handling of multiple variant types.
    """

    called_variants_dna_short_read_id = models.CharField(
        max_length=255, primary_key=True
    )
    aligned_dna_short_read_set_id = models.ForeignKey(
        AlignedDNAShortReadSet, on_delete=models.CASCADE
    )
    called_variants_dna_file = models.CharField(max_length=255, unique=True)
    md5sum = models.CharField(max_length=32, unique=True)
    caller_software = models.CharField(max_length=255)
    variant_types = models.CharField(max_length=255, choices=VariantType.choices)
    analysis_details = models.TextField(
        blank=True,
        null=True,
        help_text="brief description of the analysis pipeline used for "
        + "producing the file; perhaps a link to something like a WDL"
        + "file or github repository",
    )

    def __str__(self):
        return self.called_variants_dna_short_read_id


class ExperimentRNAShortRead(models.Model):
    experiment_rna_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for experiment_rna_short_read (primary key).",
    )
    analyte = models.ForeignKey(
        "Analyte",
        on_delete=models.CASCADE,
        help_text="Reference to the analyte ID from which this experiment derives.",
    )
    experiment_sample_id = models.CharField(
        max_length=255,
        help_text="Identifier used in the data file, such as the SM tag in a BAM header or column headers for genotype fields in a VCF file.",
    )
    seq_library_prep_kit_method = models.CharField(
        max_length=255,
        blank=True,
        help_text="Library prep kit used, can be missing if RC receives external data.",
    )
    library_prep_type = models.CharField(
        max_length=255,
        choices=[
            ("stranded poly-A pulldown", "Stranded Poly-A Pulldown"),
            ("stranded total RNA", "Stranded Total RNA"),
            ("rRNA depletion", "rRNA Depletion"),
            ("globin depletion", "Globin Depletion"),
        ],
        help_text="Type of library prep used.",
    )
    experiment_type = models.CharField(
        max_length=255,
        choices=[
            ("single-end", "Single-End"),
            ("paired-end", "Paired-End"),
            ("targeted", "Targeted"),
            ("untargeted", "Untargeted"),
        ],
        help_text="Type of RNA sequencing experiment.",
    )
    read_length = models.IntegerField(
        help_text="Sequenced read length in base pairs; GREGoR RCs do paired end sequencing, so 100bp indicates 2x100bp."
    )
    single_or_paired_ends = models.CharField(
        max_length=255,
        choices=[("single-end", "Single-End"), ("paired-end", "Paired-End")],
        help_text="Specifies if the sequencing was single or paired end.",
    )
    date_data_generation = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the data was generated; format should follow ISO 8601 (YYYY-MM-DD).",
    )
    sequencing_platform = models.CharField(
        max_length=255,
        blank=True,
        help_text="Sequencing platform used for the experiment.",
    )
    within_site_batch_name = models.CharField(
        max_length=255,
        help_text="Batch number for the site, important for future batch correction.",
    )
    RIN = models.FloatField(
        null=True, blank=True, help_text="RIN number for quality of sample."
    )
    estimated_library_size = models.FloatField(
        null=True, blank=True, help_text="Estimated size of the library."
    )
    total_reads = models.FloatField(
        null=True,
        blank=True,
        help_text="Total number of reads; should be input as an integer despite the float type.",
    )
    percent_rRNA = models.FloatField(
        null=True, blank=True, help_text="Percentage of rRNA."
    )
    percent_mRNA = models.FloatField(
        null=True, blank=True, help_text="Percentage of mRNA."
    )
    percent_mtRNA = models.FloatField(
        null=True, blank=True, help_text="Percentage of mtRNA."
    )
    percent_Globin = models.FloatField(
        null=True, blank=True, help_text="Percentage of Globin."
    )
    percent_UMI = models.FloatField(
        null=True,
        blank=True,
        help_text="Percentage of UMI (Unique Molecular Identifier).",
    )
    five_prime_three_prime_bias = models.FloatField(
        null=True, blank=True, help_text="5' to 3' bias of sequencing."
    )
    percent_GC = models.FloatField(
        null=True, blank=True, help_text="GC content percentage."
    )
    percent_chrX_Y = models.FloatField(
        null=True, blank=True, help_text="Percentage of reads from chromosome X and Y."
    )

    def __str__(self):
        return self.experiment_rna_short_read_id


class AlignedRNAShortRead(models.Model):
    aligned_rna_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for aligned_short_read (primary key).",
    )
    experiment_rna_short_read = models.ForeignKey(
        "ExperimentRNAShortRead",
        on_delete=models.CASCADE,
        help_text="Identifier for experiment.",
    )
    aligned_rna_short_read_file = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name and path of file with aligned reads.",
    )
    aligned_rna_short_read_index_file = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name and path of index file corresponding to aligned reads file.",
    )
    md5sum = models.CharField(
        max_length=255, unique=True, help_text="MD5 checksum for file."
    )
    reference_assembly = models.CharField(
        max_length=50,
        choices=[
            ("GRCh38", "GRCh38"),
            ("GRCh37", "GRCh37"),
            ("NCBI36", "NCBI36"),
            ("NCBI35", "NCBI35"),
            ("NCBI34", "NCBI34"),
        ],
        help_text="Reference genome assembly used.",
    )
    reference_assembly_uri = models.URLField(
        help_text="URI for reference assembly file."
    )
    reference_assembly_details = models.TextField(
        help_text="Details about the reference assembly used."
    )
    gene_annotation = models.CharField(
        max_length=255, help_text="Annotation file used for alignment."
    )
    gene_annotation_details = models.TextField(
        help_text="Detailed description of gene annotation used."
    )
    alignment_software = models.CharField(
        max_length=255,
        help_text="Software including version number used for alignment.",
    )
    alignment_log_file = models.CharField(
        max_length=255,
        help_text="Path of (log) file with all parameters for alignment software.",
    )
    alignment_postprocessing = models.TextField(
        help_text="Post processing applied to alignment."
    )
    mean_coverage = models.FloatField(
        help_text="Mean coverage of either the genome or the targeted regions."
    )
    percent_uniquely_aligned = models.FloatField(
        help_text="Percentage of reads that aligned to just one place."
    )
    percent_multimapped = models.FloatField(
        help_text="Percentage of reads that aligned to multiple places."
    )
    percent_unaligned = models.FloatField(
        help_text="Percentage of reads that didn't align."
    )
    quality_issues = models.TextField(
        help_text="Any QC issues that would be important to note."
    )

    def __str__(self):
        return self.aligned_rna_short_read_id


class ExperimentNanopore(models.Model):
    experiment_nanopore_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for experiment_nanopore (primary key).",
    )
    analyte = models.ForeignKey(
        "Analyte",
        on_delete=models.CASCADE,
        help_text="Identifier for the analyte used in the experiment.",
    )
    experiment_sample_id = models.CharField(
        max_length=255, help_text="Identifier used in the data file."
    )
    seq_library_prep_kit_method = models.CharField(
        max_length=255,
        choices=[
            ("LSK109", "LSK109"),
            ("LSK110", "LSK110"),
            ("LSK111", "LSK111"),
            ("Kit 14", "Kit 14"),
            ("Rapid", "Rapid"),
            ("Rapid kit 14", "Rapid kit 14"),
            ("Unknown", "Unknown"),
        ],
        help_text="Library prep kit used.",
    )
    fragmentation_method = models.TextField(
        help_text="Method used for shearing/fragmentation."
    )
    experiment_type = models.CharField(
        max_length=255,
        choices=[("targeted", "targeted"), ("genome", "genome")],
        help_text="Type of experiment.",
    )
    targeted_regions_method = models.TextField(help_text="Capture method used.")
    targeted_region_bed_file = models.URLField(
        help_text="Name and path of bed file uploaded to workspace."
    )
    date_data_generation = models.DateField(help_text="Date of data generation.")
    sequencing_platform = models.CharField(
        max_length=255,
        choices=[
            ("Oxford Nanopore PromethION 48", "Oxford Nanopore PromethION 48"),
            ("Oxford Nanopore PromethION 24", "Oxford Nanopore PromethION 24"),
            ("Oxford Nanopore PromethION P2", "Oxford Nanopore PromethION P2"),
            (
                "Oxford Nanopore PromethION P2 Solo",
                "Oxford Nanopore PromethION P2 Solo",
            ),
            ("Oxford Nanopore MinION Mk1C", "Oxford Nanopore MinION Mk1C"),
            ("Oxford Nanopore MinION Mk1B", "Oxford Nanopore MinION Mk1B"),
            ("Oxford Nanopore Flongle", "Oxford Nanopore Flongle"),
        ],
        help_text="Sequencing platform used for the experiment.",
    )
    chemistry_type = models.CharField(
        max_length=255,
        choices=[("R9.4.1", "R9.4.1"), ("R10.4.1", "R10.4.1")],
        help_text="Chemistry type used for the experiment.",
    )
    was_barcoded = models.BooleanField(
        default=False,
        help_text="Indicates whether samples were barcoded on this flowcell.",
    )
    barcode_kit = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of the kit used for barcoding.",
    )

    def __str__(self):
        return self.experiment_nanopore_id


class AlignedNanopore(models.Model):
    aligned_nanopore_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for aligned_nanopore (primary key).",
    )
    experiment_nanopore = models.ForeignKey(
        "ExperimentNanopore",
        on_delete=models.CASCADE,
        help_text="Identifier for experiment, referencing the experiment_nanopore_id from the experiment_nanopore table.",
    )
    aligned_nanopore_file = models.URLField(
        unique=True,
        help_text="Name and path of file with aligned reads. This must be a unique path.",
    )
    aligned_nanopore_index_file = models.URLField(
        unique=True,
        help_text="Name and path of index file corresponding to aligned reads file. This must be a unique path.",
    )
    md5sum = models.CharField(
        max_length=255,
        unique=True,
        help_text="MD5 checksum for the file, ensuring file integrity.",
    )
    reference_assembly = models.CharField(
        max_length=50,
        choices=[
            ("chm13", "chm13"),
            ("GRCh38_noalt", "GRCh38_noalt"),
            ("GRCh38", "GRCh38"),
            ("GRCh37", "GRCh37"),
            ("NCBI36", "NCBI36"),
            ("NCBI35", "NCBI35"),
            ("NCBI34", "NCBI34"),
        ],
        help_text="Reference assembly used for the alignment.",
    )
    alignment_software = models.CharField(
        max_length=255,
        help_text="Software including version number used for alignment.",
    )
    analysis_details = models.TextField(
        help_text="Brief description of the analysis pipeline used for producing the file."
    )
    mean_coverage = models.FloatField(
        help_text="Mean coverage of either the genome or the targeted regions."
    )
    genome_coverage = models.IntegerField(
        help_text="Percentage of the genome covered at a certain depth (e.g., >=90% at 10x or 20x)."
    )
    contamination = models.FloatField(
        help_text="Contamination level estimate, e.g., <1% (display raw fraction not percent)."
    )
    sex_concordance = models.BooleanField(
        help_text="Comparison between reported sex vs genotype sex."
    )
    num_reads = models.IntegerField(help_text="Total reads before ignoring alignment.")
    num_bases = models.IntegerField(
        help_text="Number of bases before ignoring alignment."
    )
    read_length_mean = models.IntegerField(
        help_text="Mean length of all reads before ignoring alignment."
    )
    num_aligned_reads = models.IntegerField(help_text="Total aligned reads.")
    num_aligned_bases = models.IntegerField(
        help_text="Number of bases in aligned reads."
    )
    aligned_read_length_mean = models.IntegerField(
        help_text="Mean length of aligned reads."
    )
    read_error_rate = models.FloatField(
        help_text="Mean empirical per-base error rate of aligned reads."
    )
    mapped_reads_pct = models.FloatField(
        help_text="Number between 1 and 100, representing the percentage of reads that mapped to the reference."
    )
    methylation_called = models.BooleanField(
        help_text="Indicates whether 5mC and 6mA methylation has been called and annotated in the BAM file's MM and ML tags."
    )
    quality_issues = models.TextField(
        help_text="Describe if there are any QC issues that would be important to note."
    )

    def __str__(self):
        return self.aligned_nanopore_id


class AlignedNanoporeSet(models.Model):
    aligned_nanopore_set_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for a set of experiments (primary key). RCs make their own IDs (these must begin with center-specific prefix). This ID links the aligned_nanopore table to the called_variants_nanopore table. For centers that are only uploading single sample files, the aligned_nanopore_set_id and aligned_nanopore_id values can be identical. For centers uploading multi-sample files, they will need to come up with a value for aligned_nanopore_set_id that makes sense to them for indicating the sample group for a multi-sample callset, and use that same value in called_variants_nanopore.",
    )
    aligned_nanopore = models.ForeignKey(
        "AlignedNanopore",
        on_delete=models.CASCADE,
        help_text="The identifier for a single-sample aligned_nanopore included in the read set (one per row). This refers to IDs from the aligned_nanopore table.",
    )

    def __str__(self):
        return self.aligned_nanopore_set_id


class CalledVariantsNanopore(models.Model):
    called_variants_nanopore_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique key for table (anvil requirement).",
    )
    aligned_nanopore_set = models.ForeignKey(
        "AlignedNanoporeSet",
        on_delete=models.CASCADE,
        help_text="Identifier for experiment set. This refers to IDs from the aligned_nanopore_set table.",
    )
    called_variants_dna_file = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name and path of the file with variant calls. Stored as a unique bucket path.",
    )
    md5sum = models.CharField(
        max_length=255,
        unique=True,
        help_text="MD5 checksum for file, computed prior to upload to verify file integrity.",
    )
    caller_software = models.CharField(
        max_length=255,
        help_text="Variant calling software used including version number.",
    )
    variant_types = models.CharField(
        max_length=255,
        help_text="Types of variants called, separated by '|'. Can include types such as SNV, INDEL, SV, CNV, RE, and MEI.",
    )
    analysis_details = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of the analysis pipeline used for producing the file; perhaps a link to something like a WDL file or GitHub repository.",
    )

    def __str__(self):
        return self.called_variants_nanopore_id


class ExperimentPacBio(models.Model):
    experiment_pac_bio_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="identifier for experiment_short_read (primary key)",
    )
    analyte = models.ForeignKey(
        "Analyte",
        on_delete=models.CASCADE,
        help_text="Analyte identifier linked to the ExperimentPacBio",
    )
    experiment_sample_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="identifier used in the data file (e.g., the SM tag in a BAM header, column headers for genotype fields in a VCF file)",
    )
    seq_library_prep_kit_method = models.CharField(
        max_length=255,
        choices=[
            ("SMRTbell prep kit 3.0", "SMRTbell prep kit 3.0"),
            (
                "HiFI express template prep kit 2.0",
                "HiFI express template prep kit 2.0",
            ),
        ],
        help_text="Library prep kit used",
    )
    fragmentation_method = models.CharField(
        max_length=255, blank=True, help_text="method used for shearing/fragmentation"
    )
    experiment_type = models.CharField(
        max_length=50,
        choices=[
            ("targeted", "targeted"),
            ("genome", "genome"),
            ("fiberseq", "fiberseq"),
            ("isoseq", "isoseq"),
            ("masseq", "masseq"),
        ],
        help_text="Type of experiment conducted",
    )
    targeted_regions_method = models.CharField(
        max_length=255, blank=True, help_text="Capture method used."
    )
    targeted_region_bed_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="name and path of bed file uploaded to workspace",
    )
    date_data_generation = models.DateField(
        null=True,
        blank=True,
        help_text="Date of data generation (First sequencing date)",
    )
    sequencing_platform = models.CharField(
        max_length=255,
        choices=[
            ("PacBio Revio", "PacBio Revio"),
            ("PacBio Sequel IIe", "PacBio Sequel IIe"),
            ("PacBio Sequel II", "PacBio Sequel II"),
        ],
        help_text="sequencing platform used for the experiment",
    )
    was_barcoded = models.BooleanField(
        default=False,
        help_text="indicates whether samples were barcoded on this flowcell",
    )
    barcode_kit = models.CharField(
        max_length=255, blank=True, help_text="Barcode kit used"
    )
    application_kit = models.CharField(
        max_length=255,
        blank=True,
        help_text="Library prep kits for special applications",
    )
    smrtlink_server_version = models.CharField(
        max_length=255, help_text="Version number of PacBio SMRTLink software"
    )
    instrument_ics_version = models.CharField(
        max_length=255, help_text="Version number of PacBio instrument control software"
    )
    size_selection_method = models.CharField(
        max_length=255, blank=True, help_text="method use for library size selection"
    )
    library_size = models.CharField(
        max_length=255, blank=True, help_text="expected size of library from FemtoPulse"
    )
    smrt_cell_kit = models.CharField(
        max_length=255, blank=True, help_text="part number of the SMRT Cell"
    )
    smrt_cell_id = models.CharField(
        max_length=255, blank=True, help_text="unique serial number for SMRT Cell"
    )
    movie_name = models.CharField(
        max_length=255, blank=True, help_text="unique name of sequencing collection"
    )
    polymerase_kit = models.CharField(
        max_length=255, blank=True, help_text="part number of polymerase kit used"
    )
    sequencing_kit = models.CharField(
        max_length=255, blank=True, help_text="part number of sequencing kit reagents"
    )
    movie_length_hours = models.FloatField(
        null=True, blank=True, help_text="length of sequencing collection, in hrs"
    )
    includes_kinetics = models.BooleanField(
        default=False, help_text="run reports base kinetics"
    )
    includes_CpG_methylation = models.BooleanField(
        default=False, help_text="run reports CpG methylation"
    )
    by_strand = models.BooleanField(
        default=False, help_text="run reports separate reads per strand"
    )


class AlignedPacBio(models.Model):
    aligned_pac_bio_id = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
        help_text="identifier for aligned_short_read (primary key)",
    )
    experiment_pac_bio = models.ForeignKey(
        "ExperimentPacBio",
        on_delete=models.CASCADE,
        help_text="identifier for experiment",
    )
    aligned_pac_bio_file = models.URLField(
        help_text="name and path of file with aligned reads"
    )
    aligned_pac_bio_index_file = models.URLField(
        help_text="name and path of index file corresponding to aligned reads file"
    )
    md5sum = models.CharField(
        max_length=32, unique=True, help_text="md5 checksum for file"
    )
    reference_assembly = models.CharField(
        max_length=50,
        choices=[
            ("chm13", "chm13"),
            ("GRCh38_noalt", "GRCh38_noalt"),
            ("GRCh38", "GRCh38"),
            ("GRCh37", "GRCh37"),
            ("NCBI36", "NCBI36"),
            ("NCBI35", "NCBI35"),
            ("NCBI34", "NCBI34"),
        ],
        help_text="Reference assembly used",
    )
    alignment_software = models.CharField(
        max_length=255, help_text="Software including version number used for alignment"
    )
    analysis_details = models.TextField(
        help_text="brief description of the analysis pipeline used for producing the file"
    )
    mean_coverage = models.FloatField(
        help_text="Mean coverage of either the genome or the targeted regions"
    )
    genome_coverage = models.IntegerField(
        help_text="e.g. ≥90% at 10x or 20x; per consortium decision"
    )
    contamination = models.FloatField(
        help_text="Contamination level estimate., e.g. <1% (display raw fraction not percent)"
    )
    sex_concordance = models.BooleanField(
        help_text="Comparison between reported sex vs genotype sex"
    )
    num_reads = models.IntegerField(help_text="Total reads (before/ignoring alignment)")
    num_bases = models.IntegerField(
        help_text="Number of bases (before/ignoring alignment)"
    )
    read_length_mean = models.IntegerField(
        help_text="Mean length of all reads (before/ignoring alignment)"
    )
    num_aligned_reads = models.IntegerField(help_text="Total aligned reads")
    num_aligned_bases = models.IntegerField(
        help_text="Number of bases in aligned reads"
    )
    aligned_read_length_mean = models.IntegerField(
        help_text="Mean length of aligned reads"
    )
    read_error_rate = models.FloatField(
        help_text="Mean empirical per-base error rate of aligned reads"
    )
    mapped_reads_pct = models.FloatField(
        help_text="Number between 1 and 100, representing the percentage of mapped reads"
    )
    methylation_called = models.BooleanField(
        help_text="Indicates whether 5mC and 6mA methylation has been called and annotated in the BAM file's MM and ML tags"
    )


class AlignedPacBioSet(models.Model):
    aligned_pac_bio_set_id = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
        help_text="Identifier for a set of experiments (primary key). RCs make their own IDs (these must begin with center-specific prefix). For centers that are only uploading single sample files, the aligned_short_read_set_id and aligned_short_read_id values can be identical. For centers uploading multi-sample files, they will need to come up with a value for aligned_short_read_set_id that makes sense to them for indicating the sample group for a multi-sample callset, and use that same value in called_variants_short_read.",
    )
    aligned_pac_bio = models.ForeignKey(
        "AlignedPacBio",
        on_delete=models.CASCADE,
        help_text="The identifier for a single-sample aligned_pac_bio included in the read set (one per row).",
    )

    def __str__(self):
        return self.aligned_pac_bio_set_id


class CalledVariantsPacBio(models.Model):
    called_variants_pac_bio_id = models.CharField(
        max_length=255,
        unique=True,
        primary_key=True,
        help_text="Unique key for table (ANVIL requirement).",
    )
    aligned_pac_bio_set = models.ForeignKey(
        "AlignedPacBioSet",
        on_delete=models.CASCADE,
        help_text="Identifier for experiment set.",
    )
    called_variants_dna_file = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name and path of the file with variant calls. Stored on Google Cloud Storage (gs://).",
    )
    md5sum = models.CharField(
        max_length=32,
        unique=True,
        help_text="MD5 checksum for file. md5sum computed prior to upload (used to verify file integrity).",
    )
    caller_software = models.CharField(
        max_length=255,
        help_text="Variant calling software used including version number.",
    )
    variant_types = models.CharField(
        max_length=255,
        help_text="Types of variants called. SNV, INDEL, SV, CNV, RE, MEI. If there are two VCFs for SNV and Indels, there would be two different lines in this table; if combined in one VCF, a |-delimited entry.",
    )
    analysis_details = models.TextField(
        blank=True,
        help_text="Brief description of the analysis pipeline used for producing the file; perhaps a link to something like a WDL file or github repository.",
    )

    def __str__(self):
        return self.called_variants_pac_bio_id


class ExperimentATACShortRead(models.Model):
    experiment_atac_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for experiment_atac_short_read (primary key). RCs make their own IDs, must begin with center abbreviation as defined in participant table; need to be globally unique in consortium; may be generated by prepending experiment_sample_id with center abbreviation.",
    )
    analyte_id = models.ForeignKey(
        "Analyte", on_delete=models.CASCADE, help_text="Reference to analyte ID."
    )
    experiment_sample_id = models.CharField(
        max_length=255,
        help_text="Identifier used in the data file (e.g., the SM tag in a BAM header, column headers for genotype fields in a VCF file). May be the same as experiment_short_read_id if the file does contain sample identifiers. Should be present if downstream file contains a sample_id (e.g., BAM, VCF). Some centers have one id for the sample (tube) and a different ID for the sample as named in the VCF.",
    )
    seq_library_prep_kit_method = models.CharField(
        max_length=255,
        help_text="Library prep kit used. Can be missing if RC receives external data.",
    )
    read_length = models.IntegerField(
        help_text="Sequenced read length (bp); GREGoR RCs do paired end sequencing, so is the example of 100bp indicates 2x100bp. Can be missing if RC receives external data; all RCs are doing paired-end reads."
    )
    experiment_type = models.CharField(
        max_length=255,
        choices=[("targeted", "Targeted"), ("genome", "Genome"), ("exome", "Exome")],
        help_text="Type of experiment. Facilitates having exome and GS-SR experiments in the same experiment_details table.",
    )
    targeted_regions_method = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Which capture kit is used. Can be missing if RC receives external data.",
    )
    targeted_region_bed_file = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name and path of bed file uploaded to workspace. Can be missing if RC receives external data.",
    )
    date_data_generation = models.DateField(
        help_text="Date of data generation (First sequencing date). Can be missing if RC receives external data; ISO 8601 date format."
    )
    target_insert_size = models.IntegerField(
        blank=True,
        null=True,
        help_text="Insert size the protocol targets for DNA fragments. Can be missing if RC receives external data.",
    )
    sequencing_platform = models.CharField(
        max_length=255,
        help_text="Sequencing platform used for the experiment. Can be missing if RC receives external data.",
    )

    def __str__(self):
        return self.experiment_atac_short_read_id


class AlignedATACShortRead(models.Model):
    aligned_atac_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for aligned_atac_short_read (primary key). Experiment_short_read_id + alignment indicator.",
    )
    experiment_atac_short_read = models.ForeignKey(
        "ExperimentATACShortRead",
        on_delete=models.CASCADE,
        help_text="Identifier for experiment. Reference to experiment_atac_short_read.experiment_atac_short_read_id.",
    )
    aligned_atac_short_read_file = models.URLField(
        max_length=1024,
        unique=True,
        help_text="Name and path of file with aligned reads.",
    )
    aligned_atac_short_read_index_file = models.URLField(
        max_length=1024,
        unique=True,
        help_text="Name and path of index file corresponding to aligned reads file.",
    )
    md5sum = models.CharField(
        max_length=255, unique=True, help_text="MD5 checksum for file."
    )
    reference_assembly = models.CharField(
        max_length=50,
        choices=[
            ("GRCh38", "GRCh38"),
            ("GRCh37", "GRCh37"),
            ("NCBI36", "NCBI36"),
            ("NCBI35", "NCBI35"),
            ("NCBI34", "NCBI34"),
        ],
        help_text="Reference assembly used.",
    )
    reference_assembly_uri = models.URLField(max_length=1024, blank=True, null=True)
    reference_assembly_details = models.TextField(blank=True, null=True)
    alignment_software = models.CharField(
        max_length=255, help_text="Software including version number."
    )
    gene_annotation_details = models.CharField(max_length=255, blank=True, null=True)
    alignment_log_file = models.URLField(max_length=1024, blank=True, null=True)
    alignment_postprocessing = models.TextField(blank=True, null=True)
    mean_coverage = models.FloatField(
        help_text="Mean coverage of either the genome or the targeted regions."
    )
    percent_uniquely_aligned = models.FloatField(
        help_text="How many reads aligned to just one place."
    )
    percent_multimapped = models.FloatField(
        help_text="How many reads aligned to multiple places."
    )
    percent_unaligned = models.FloatField(help_text="How many reads didn't align.")

    def __str__(self):
        return self.aligned_atac_short_read_id


class CalledPeaksATACShortRead(models.Model):
    called_peaks_atac_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique key for table (anvil requirement).",
    )
    aligned_atac_short_read = models.OneToOneField(
        "AlignedATACShortRead",
        on_delete=models.CASCADE,
        help_text="Identifier for aligned ATAC-seq data.",
    )
    called_peaks_file = models.URLField(
        max_length=1024,
        unique=True,
        help_text="Name and path of the bed file with open chromatin peaks after QC filtering.",
    )
    peaks_md5sum = models.CharField(
        max_length=255, unique=True, help_text="MD5 checksum for called_peaks_file."
    )
    peak_caller_software = models.CharField(
        max_length=255, help_text="Peak calling software used including version number."
    )
    peak_set_type = models.CharField(
        max_length=50,
        choices=[
            ("narrowPeak", "narrowPeak"),
            ("gappedPeak", "gappedPeak"),
            ("IDR", "IDR"),
        ],
        help_text="Peak set type, according to ENCODE descriptors.",
    )
    analysis_details = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of the analysis pipeline used for producing the called_peaks_file.",
    )

    def __str__(self):
        return self.called_peaks_atac_short_read_id

class AlleleSpecificATACShortRead(models.Model):
    asc_atac_short_read_id = models.CharField(max_length=255, primary_key=True, help_text="Unique key for table (anvil requirement).")
    called_peaks_atac_short_read = models.ForeignKey('CalledPeaksATACShortRead', on_delete=models.CASCADE, help_text="Identifier for called peaks.")
    asc_file = models.URLField(max_length=1024, unique=True, help_text="Name and path of the tsv file with allele-specific chromatin accessibility measures (logFC) at heterozygous sites after QC and significance testing.")
    asc_md5sum = models.CharField(max_length=255, unique=True, help_text="MD5 checksum for called_peaks_file.")
    peak_set_type = models.CharField(max_length=50, choices=[('narrowPeak', 'narrowPeak'), ('gappedPeak', 'gappedPeak'), ('IDR', 'IDR')], help_text="Peak set type, according to ENCODE descriptors.")
    het_sites_file = models.URLField(max_length=1024, unique=True, help_text="VCF file containing prefiltered heterozygous sites used for reference alignment bias testing and calling allele-specific chromatin accessibility events.")
    het_sites_md5sum = models.CharField(max_length=255, unique=True, help_text="MD5 checksum for het_sites_file.")
    analysis_details = models.TextField(blank=True, null=True, help_text="Brief description of the analysis pipeline used for producing the asc_file.")

    def __str__(self):
        return self.asc_atac_short_read_id
