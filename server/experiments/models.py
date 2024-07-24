#!/usr/bin/env python
# experiments/models.py

"""
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from metadata.models import Analyte, Participant, VariantType
from config.selectors import validate_cloud_url


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
    participant_id = models.ForeignKey(
        Participant,
        to_field="participant_id",
        db_column="participant_id",
        on_delete=models.CASCADE,
        related_name="experiments",
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
    participant_id = models.ForeignKey(
        Participant,
        to_field="participant_id",
        db_column="participant_id",
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
    analyte_id = models.ForeignKey(
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
    experiment_dna_short_read_id = models.ForeignKey(
        "ExperimentDNAShortRead",
        on_delete=models.CASCADE,
        to_field="experiment_dna_short_read_id",
        db_column="experiment_dna_short_read_id",
    )
    aligned_dna_short_read_file = models.CharField(
        max_length=1024, validators=[validate_cloud_url]
    )
    aligned_dna_short_read_index_file = models.CharField(
        max_length=1024, validators=[validate_cloud_url]
    )
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

class LibraryPrepType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name


class ExperimentType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)

    def __str__(self):
        return self.display_name


class ExperimentRNAShortRead(models.Model):
    experiment_rna_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Identifier for experiment_rna_short_read (primary key).",
    )
    analyte_id = models.ForeignKey(
        Analyte,
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
    library_prep_type = models.ManyToManyField(
        "LibraryPrepType",
        blank= True,
        help_text="Type of library prep used.",
    )
    experiment_type = models.ManyToManyField(
        "ExperimentType",
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
    experiment_rna_short_read_id = models.ForeignKey(
        "ExperimentRNAShortRead",
        to_field="experiment_rna_short_read_id",
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
        blank=True, null=True,
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
        max_length=255, blank=True, null=True,
        help_text="Path of (log) file with all parameters for alignment software.",
    )
    alignment_postprocessing = models.TextField(
        blank=True, null=True,
        help_text="Post processing applied to alignment."
    )
    mean_coverage = models.FloatField(
        null=True,
        help_text="Mean coverage of either the genome or the targeted regions."
    )
    percent_uniquely_aligned = models.FloatField(
        null=True,
        help_text="Percentage of reads that aligned to just one place."
    )
    percent_multimapped = models.FloatField(
        null=True,
        help_text="Percentage of reads that aligned to multiple places."
    )
    percent_unaligned = models.FloatField(
        null=True,
        help_text="Percentage of reads that didn't align."
    )
    quality_issues = models.TextField(
        blank=True, null=True,
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
    analyte_id = models.ForeignKey(
        Analyte,
        to_field="analyte_id",
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
        blank=True, null=True, help_text="Method used for shearing/fragmentation."
    )
    experiment_type = models.CharField(
        max_length=255,
        choices=[("targeted", "targeted"), ("genome", "genome")],
        help_text="Type of experiment.",
    )
    targeted_regions_method = models.TextField(
        blank=True, null=True, help_text="Capture method used."
    )
    targeted_region_bed_file = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        validators=[validate_cloud_url],
        help_text="Name and path of bed file uploaded to workspace.",
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
    experiment_nanopore_id = models.ForeignKey(
        "ExperimentNanopore",
        to_field="experiment_nanopore_id",
        on_delete=models.CASCADE,
        help_text="Identifier for experiment, referencing the experiment_nanopore_id from the experiment_nanopore table.",
    )
    aligned_nanopore_file = models.CharField(
        unique=True,
        max_length=1024,
        validators=[validate_cloud_url],
        help_text="Name and path of file with aligned reads. This must be a unique path.",
    )
    aligned_nanopore_index_file = models.CharField(
        unique=True,
        max_length=1024,
        validators=[validate_cloud_url],
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
        blank=True,
        null=True,
        help_text="Brief description of the analysis pipeline used for producing the file.",
    )
    mean_coverage = models.FloatField(
        blank=True,
        null=True,
        help_text="Mean coverage of either the genome or the targeted regions.",
    )
    genome_coverage = models.IntegerField(
        blank=True,
        null=True,
        help_text="Percentage of the genome covered at a certain depth (e.g., >=90% at 10x or 20x).",
    )
    contamination = models.FloatField(
        blank=True,
        null=True,
        help_text="Contamination level estimate, e.g., <1% (display raw fraction not percent).",
    )
    sex_concordance = models.BooleanField(
        blank=True,
        null=True,
        help_text="Comparison between reported sex vs genotype sex.",
    )
    num_reads = models.IntegerField(
        blank=True, null=True, help_text="Total reads before ignoring alignment."
    )
    num_bases = models.IntegerField(
        blank=True, null=True, help_text="Number of bases before ignoring alignment."
    )
    read_length_mean = models.IntegerField(
        blank=True,
        null=True,
        help_text="Mean length of all reads before ignoring alignment.",
    )
    num_aligned_reads = models.IntegerField(
        blank=True, null=True, help_text="Total aligned reads."
    )
    num_aligned_bases = models.IntegerField(
        blank=True, null=True, help_text="Number of bases in aligned reads."
    )
    aligned_read_length_mean = models.IntegerField(
        blank=True, null=True, help_text="Mean length of aligned reads."
    )
    read_error_rate = models.FloatField(
        blank=True,
        null=True,
        help_text="Mean empirical per-base error rate of aligned reads.",
    )
    mapped_reads_pct = models.FloatField(
        blank=True,
        null=True,
        help_text="Number between 1 and 100, representing the percentage of reads that mapped to the reference.",
    )
    methylation_called = models.BooleanField(
        help_text="Indicates whether 5mC and 6mA methylation has been called and annotated in the BAM file's MM and ML tags."
    )
    quality_issues = models.TextField(
        blank=True,
        null=True,
        help_text="Describe if there are any QC issues that would be important to note.",
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
    analyte_id = models.ForeignKey(
        Analyte,
        to_field="analyte_id",
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
    experiment_pac_bio_id = models.ForeignKey(
        "ExperimentPacBio",
        to_field="experiment_pac_bio_id",
        on_delete=models.CASCADE,
        help_text="identifier for experiment",
    )
    aligned_pac_bio_file = models.CharField(
        max_length=1024,
        validators=[validate_cloud_url],
        help_text="name and path of file with aligned reads",
    )
    aligned_pac_bio_index_file = models.CharField(
        max_length=1024,
        validators=[validate_cloud_url],
        help_text="name and path of index file corresponding to aligned reads file",
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
        blank=True,
        null=True,
        help_text="brief description of the analysis pipeline used for producing the file",
    )
    mean_coverage = models.FloatField(
        blank=True,
        null=True,
        help_text="Mean coverage of either the genome or the targeted regions",
    )
    genome_coverage = models.IntegerField(
        blank=True,
        null=True,
        help_text="e.g. ≥90% at 10x or 20x; per consortium decision",
    )
    contamination = models.FloatField(
        blank=True,
        null=True,
        help_text="Contamination level estimate., e.g. <1% (display raw fraction not percent)",
    )
    sex_concordance = models.BooleanField(
        blank=True,
        null=True,
        help_text="Comparison between reported sex vs genotype sex",
    )
    num_reads = models.IntegerField(
        blank=True, null=True, help_text="Total reads (before/ignoring alignment)"
    )
    num_bases = models.IntegerField(
        blank=True, null=True, help_text="Number of bases (before/ignoring alignment)"
    )
    read_length_mean = models.IntegerField(
        blank=True,
        null=True,
        help_text="Mean length of all reads (before/ignoring alignment)",
    )
    num_aligned_reads = models.IntegerField(
        blank=True, null=True, help_text="Total aligned reads"
    )
    num_aligned_bases = models.IntegerField(
        blank=True, null=True, help_text="Number of bases in aligned reads"
    )
    aligned_read_length_mean = models.IntegerField(
        blank=True, null=True, help_text="Mean length of aligned reads"
    )
    read_error_rate = models.FloatField(
        blank=True,
        null=True,
        help_text="Mean empirical per-base error rate of aligned reads",
    )
    mapped_reads_pct = models.FloatField(
        blank=True,
        null=True,
        help_text="Number between 1 and 100, representing the percentage of mapped reads",
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
        Analyte, on_delete=models.CASCADE, help_text="Reference to analyte ID."
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
    asc_atac_short_read_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Unique key for table (anvil requirement).",
    )
    called_peaks_atac_short_read = models.ForeignKey(
        "CalledPeaksATACShortRead",
        on_delete=models.CASCADE,
        help_text="Identifier for called peaks.",
    )
    asc_file = models.URLField(
        max_length=1024,
        unique=True,
        help_text="Name and path of the tsv file with allele-specific chromatin accessibility measures (logFC) at heterozygous sites after QC and significance testing.",
    )
    asc_md5sum = models.CharField(
        max_length=255, unique=True, help_text="MD5 checksum for called_peaks_file."
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
    het_sites_file = models.URLField(
        max_length=1024,
        unique=True,
        help_text="VCF file containing prefiltered heterozygous sites used for reference alignment bias testing and calling allele-specific chromatin accessibility events.",
    )
    het_sites_md5sum = models.CharField(
        max_length=255, unique=True, help_text="MD5 checksum for het_sites_file."
    )
    analysis_details = models.TextField(
        blank=True,
        null=True,
        help_text="Brief description of the analysis pipeline used for producing the asc_file.",
    )

    def __str__(self):
        return self.asc_atac_short_read_id
