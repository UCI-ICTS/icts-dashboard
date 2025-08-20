
export const home = 
`The UC Irvine Institute for Clinical and Translational Science (ICTS) is funded by the National Institutes of Health (NIH) under the Clinical and Translational Sciences Award (CTSA) program. Currently, there are more than 50 medical research institutions throughout the United States that receive CTSA program funding.

The ICTS functions as a local centerpiece for the national program, and is dedicated to advancing scientific discovery and medical breakthroughs. Collectively, our goal is simple: to accelerate these discoveries from the lab and translate them into life-altering medical care.`

export const home2 = 
`The following tools are used to aid with data processing and discovery for the above research:
- [Pacific Biosciences HiFi human WGS WDL](https://github.com/PacificBiosciences/HiFI-human-WGS-WDL)
  - Workflow for analyzing human PacBio whole genome sequencing (WGS) data using [Workflow Description Language (WDL)](https://openwdl.org).
  - The primary workflow for processing PacBio long-read genome sequencing (LR-GS) datasets.
- [wgs-calling](https://codeberg.org/lightning-auriga/wgs-calling)
  - A short-read genome sequencing (SR-GS) [Snakemake](https://snakemake.readthedocs.io/en/stable/) workflow that takes FASTQ files and generates BAMs, VCFs, and all relevant sequencing QC reports.
  - The primary workflow for processing SR-GS datasets.
- [wgs-downstream](https://codeberg.org/lightning-auriga/wgs-downstream)
  - A collection of downstream tools run as a [Snakemake](https://snakemake.readthedocs.io/en/stable/) workflow on the output of wgs-calling.
  - Tools focus on cross-flowcell QC, CYP2D6 variant calling, repeat-expansion calling, and joint trio calling with [GLnexus](https://github.com/dnanexus-rnd/GLnexus) and recalling with [DeepTrio](https://github.com/google/deepvariant?tab=readme-ov-file#deeptrio).`
