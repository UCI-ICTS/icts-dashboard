# UCI Institute for Clinical and Translational Science (ICTS)

The UC Irvine Institute for Clinical and Translational Science (ICTS) is funded by the National Institutes of Health (NIH) under the Clinical and Translational Sciences Award (CTSA) program. Currently, there are more than 50 medical research institutions throughout the United States that receive CTSA program funding.

The ICTS functions as a local centerpiece for the national program, and is dedicated to advancing scientific discovery and medical breakthroughs. Collectively, our goal is simple: to accelerate these discoveries from the lab and translate them into life-altering medical care.

UC Irvine ICTS collaborates with the following consortiums and research networks:
- [Genomics Research to Elucidate the Genetics of Rare Diseases (GREGoR) Consortium](https://gregorconsortium.org/)
  - The GREGoR Consortium (Genomics Research to Elucidate the Genetics of Rare diseases) seeks to develop and apply approaches to discover the cause of currently unexplained rare genetic disorders.
- [Undiagnosed Diseases Network (UDN)](https://undiagnosed.hms.harvard.edu/)
  - The Undiagnosed Diseases Network (UDN) is a research study backed by the National Institutes of Health that seeks to provide answers for patients and families affected by these mysterious conditions.
- [Differences of Sex Development - Translational Research Network (DSD-TRN)](https://dsdtrn.org/)
  - Our guiding principle is that evidence-based standardization of diagnostic and treatment protocols will be associated with higher rates of definitively diagnosed DSD, reduced variation in clinical practice, enhanced patient/family healthcare-related experiences, and improved psychosocial outcomes for patients and their families.

The following tools are used to aid with data processing and discovery for the above research groups:
- [ICTS-Dashboard](https://github.com/UCI-ICTS/icts-dashboard)
  - A proof-of-concept for a genomic metadata database with API access. This provides user-level access to add/modify sample intake to data sharing.
  - Uses [Redux/React](https://react-redux.js.org/) UI for the frontend and a [Django](https://www.djangoproject.com/) webapp for the backend.
  - Currently based on the [GREGoR Data Model](https://github.com/UW-GAC/gregor_data_models) but is easily extensible through Django.
  - [Local network deployment for development and testing.](https://github.com/UCI-ICTS/icts-dashboard/blob/dev/docs/deployment/localDeployment.md)
- [Medical Information Assistant (MIA)](https://github.com/UCI-ICTS/mia)
  - A virtual HIPAA-compliant clinical consentbot that facilitates virtual conversations with patients.
  - Uses [Redux/React](https://react-redux.js.org/) UI for the frontend and a [Django](https://www.djangoproject.com/) webapp for the backend.
  - [Local network deployment for development and testing.](https://github.com/UCI-ICTS/mia/blob/dev/docs/deployment/localDeployment.md)
- [Pacific Biosciences HiFi human WGS WDL](https://github.com/PacificBiosciences/HiFI-human-WGS-WDL)
  - Workflow for analyzing human PacBio whole genome sequencing (WGS) data using [Workflow Description Language (WDL)](https://openwdl.org).
  - The primary workflow for processing PacBio long-read genome sequencing (LR-GS) datasets.
- [wgs-calling](https://codeberg.org/lightning-auriga/wgs-calling)
  - A short-read genome sequencing (SR-GS) [Snakemake](https://snakemake.readthedocs.io/en/stable/) workflow that takes FASTQ files and generates BAMs, VCFs, and all relevant sequencing QC reports.
  - The primary workflow for processing SR-GS datasets.
- [wgs-downstream](https://codeberg.org/lightning-auriga/wgs-downstream)
  - A collection of downstream tools run as a [Snakemake](https://snakemake.readthedocs.io/en/stable/) workflow on the output of wgs-calling.
  - Tools focus on cross-flowcell QC, CYP2D6 variant calling, repeat-expansion calling, and joint trio calling with [GLnexus](https://github.com/dnanexus-rnd/GLnexus) and recalling with [DeepTrio](https://github.com/google/deepvariant?tab=readme-ov-file#deeptrio).
