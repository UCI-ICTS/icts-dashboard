import React from "react";
import { Select } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { setTableView } from "../slices/dataSlice";

const { Option } = Select;

const tables = [
  { name: "Participants", schema: "participants", identifier: "participant_id" },
  { name: "Families", schema: "families", identifier: "family_id" },
  { name: "Genetic Findings", schema: "genetic_findings", identifier: "genetic_findings_id" },
  { name: "Analytes", schema: "analytes", identifier: "analyte_id" },
  { name: "Biobank Entries", schema: "biobank_entries", identifier: "biobank_id" },
  { name: "Phenotypes", schema: "phenotypes", identifier: "phenotype_id" },
  { name: "Experiments", schema: "experiments", identifier: "experiment_id" },
  { name: "Experiment Stages", schema: "experiment_stages", identifier: "experiment_stage_id" },
  { name: "DNA Short Read", schema: "experiment_dna_short_read", identifier: "experiment_dna_short_read_id" },
  { name: "RNA Short Read", schema: "experiment_rna_short_read", identifier: "experiment_rna_short_read_id" },
  { name: "PacBio", schema: "experiment_pac_bio", identifier: "experiment_pac_bio_id" },
  { name: "NanoPore", schema: "experiment_nanopore", identifier: "experiment_nanopore_id" },
  { name: "Aligned Experiments", schema: "aligned", identifier: "aligned_id" },
  { name: "Aligned DNA Short Read", schema: "aligned_dna_short_read", identifier: "aligned_dna_short_read_id" },
  { name: "Aligned NanoPore", schema: "aligned_nanopore", identifier: "aligned_nanopore_id" },
  { name: "Aligned Pac Bio", schema: "aligned_pac_bio", identifier: "aligned_pac_bio_id" },
  { name: "Aligned RNA Short Read", schema: "aligned_rna_short_read", identifier: "aligned_rna_short_read_id" },
];

const TableSelector = () => {
  const dispatch = useDispatch();
  const selected = useSelector((state) => state.data.tableView);

  const handleChange = (value) => {
    const selectedTable = tables.find((table) => table.schema === value);
    if (selectedTable) {
      dispatch(setTableView(selectedTable));
    }
  };

  return (
    <Select
      value={selected}
      onChange={handleChange}
      placeholder="Select Table"
      style={{ minWidth: 200 }}
    >
      {tables.map((table) => (
        <Option key={table.schema} value={table.schema}>
          {table.name}
        </Option>
      ))}
    </Select>
  );
};

export default TableSelector;
