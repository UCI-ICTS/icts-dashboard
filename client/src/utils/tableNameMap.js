// src/utils/tableNameMap.js

const map = {
  participants: "participant",
  families: "family",
  genetic_findings: "genetic_findings",
  analytes: "analyte",
  biobank_entries: "biobank",
  phenotypes: "phenotype",
  experiments: "experiment",
  experiment_dna_short_read: "experiment_dna_short_read",
  experiment_rna_short_read: "experiment_rna_short_read",
  experiment_pac_bio: "experiment_pac_bio",
  experiment_nanopore: "experiment_nanopore",
  aligned: "aligned",
  aligned_dna_short_read: "aligned_dna_short_read",
  aligned_nanopore: "aligned_nanopore",
  aligned_pac_bio: "aligned_pac_bio",
  aligned_rna_short_read: "aligned_rna_short_read",
};

export const getCollectionName = (table) => {
  return map[table] || null;
};

export const getTableName = (collectionName) => {
  const reverseMap = Object.entries(map).reduce((acc, [key, value]) => {
    acc[value] = key;
    return acc;
  }, {});
  return reverseMap[collectionName] || null;
};
