// components/CaseQueue.js

import "../App.css"
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Button, Table, Spin } from "antd";
import { getIdentifier } from "../utils/schemaAndTables";

export default function CaseQueue({
  selectedRow,
  setSelectedRow,
  onRow,
  queueLoading,
  setQueueLoading,
  openModal
}) {
  const dispatch = useDispatch();
  const caseData =  useSelector((state) => state.data.caseQueue)
  const rows = Array.isArray(caseData) ? caseData[0] : []
  const handleOpen = (schemaKey, record) => {
    if (openModal && record) {
      openModal("edit", { schemaKey, record });
    }
  };

  const igv_host = "http://localhost:60151";  // IGV Desktop App must be open to use this
  const merge_flag = "false";
  const genome_build = "hg38";
  const lrs_aligned_ids = [];
  const lrs_bam_uris = [];
  const lrs_bai_uris = [];
  const sr_dna_aligned_ids = [];
  const sr_dna_bam_uris = [];
  const sr_dna_bai_uris = [];
  const sr_rna_aligned_ids = [];
  const sr_rna_bam_uris = [];
  const sr_rna_bai_uris = [];
  let lrs_igv_link = ""
  let sr_dna_igv_link = ""
  let sr_rna_igv_link = ""

  for (const row of rows) {
    for (const idx in row.aligned_pac_bio) {
      const pb = row.aligned_pac_bio[idx]
      lrs_aligned_ids.push("aligned_pac_bio." + pb.aligned_pac_bio_id)
      lrs_bam_uris.push(pb.aligned_pac_bio_file)
      lrs_bai_uris.push(pb.aligned_pac_bio_index_file)
    }
    for (const idx in row.aligned_nanopore) {
      const np = row.aligned_nanopore[idx]
      lrs_aligned_ids.push("aligned_nanopore." + np.aligned_nanopore_id)
      lrs_bam_uris.push(np.aligned_nanopore_file)
      lrs_bai_uris.push(np.aligned_nanopore_index_file)
    }
    if (!lrs_aligned_ids.length) {
      lrs_igv_link = "No LRS alignments available";
    }
    else {
      lrs_igv_link = `${igv_host}/load?file=${lrs_bam_uris}&merge=${merge_flag}&genome=${genome_build}&name=${lrs_aligned_ids}`;
    }
    for (const idx in row.aligned_dna_short_read) {
      const sr_dna = row.aligned_dna_short_read[idx]
      sr_dna_aligned_ids.push("aligned_dna_short_read." + sr_dna.aligned_dna_short_read_id)
      sr_dna_bam_uris.push(sr_dna.aligned_dna_short_read_file)
      sr_dna_bai_uris.push(sr_dna.aligned_dna_short_read_index_file)
    }
    if (!sr_dna_aligned_ids.length) {
      sr_dna_igv_link = "No SR-GS alignments available";
    }
    else {
      sr_dna_igv_link = `${igv_host}/load?file=${sr_dna_bam_uris}&merge=${merge_flag}&genome=${genome_build}&name=${sr_dna_aligned_ids}`;
    }
    for (const idx in row.aligned_rna_short_read) {
      const sr_rna = row.aligned_rna_short_read[idx]
      sr_rna_aligned_ids.push("aligned_rna_short_read." + sr_rna.aligned_rna_short_read_id)
      sr_rna_bam_uris.push(sr_rna.aligned_rna_short_read_file)
      sr_rna_bai_uris.push(sr_rna.aligned_rna_short_read_index_file)
    }
    if (!sr_rna_aligned_ids.length) {
      sr_rna_igv_link = "No SR-RNA alignments available";
    }
    else {
      sr_rna_igv_link = `${igv_host}/load?file=${sr_rna_bam_uris}&merge=${merge_flag}&genome=${genome_build}&name=${sr_rna_aligned_ids}`;
    }
  }


  {queueLoading ? (
      <Spin tip="Loading related case data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
        <div style={{ minHeight: 100 }} />
      </Spin>
    ) : (<>div</>)}
  return (
    <>
    <span className="sider-header">
      <Button
        size="small"
        className="action-btn"
        onClick={() => setSelectedRow(null)}
      >Clear</Button>&nbsp;&nbsp;PacBio Case Queue for: {selectedRow.participant_id}&nbsp;&nbsp;
    </span>
    <span className="sider">
      <Button
        size="small"
        className="action-btn"
        onClick={()=> window.open(lrs_igv_link, "_blank")}
      >LR-GS IGV Session</Button>
    </span>
    <span className="sider">
      <Button
        size="small"
        className="action-btn"
        onClick={()=> window.open(sr_dna_igv_link, "_blank")}
      >SR-GS IGV Session</Button>
    </span>
    <span className="sider">
      <Button
        size="small"
        className="action-btn"
        onClick={()=> window.open(sr_rna_igv_link, "_blank")}
      >SR-RNA IGV Session</Button>
    </span>
    <Table
      className="table"
      dataSource={rows}
      rowKey="participant_id"
      onRow={onRow}
      size="small"
      columns={[
        { title: "Participant ID", key: "participant",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.participant_id || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Analysis status", key: "geneyx_status",
          render: (_, record) => {
            if (!Object.keys(record.geneyx_case).length) return "-";
            return record.geneyx_case["StatusName"]
          }
        },
        { title: "Analyst", key: "created_by",
          render: (_, record) => {
            if (!Object.keys(record.geneyx_case).length) return "-";
            return record.geneyx_case["CreatedByUser"]
          }
        },
        { title: "Second Pass Analyst", key: "modified_by",
          render: (_, record) => {
            if (!Object.keys(record.geneyx_case).length) return "-";
            return record.geneyx_case["ModifiedByUser"]
          }
        },
        { title: "GREGoR Family Size", key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "LR Case type", key: "lrs_case_type",
          render: (_, record) => {
            return record.gregor_family_structure
          }
        },
        { title: "Date result added", key: "date_created",
          render: (_, record) => {
            if (!Object.keys(record.geneyx_case).length) return "-";
            return record.geneyx_case["CreateDate"].toString().split("T")[0]
          }
        },
        { title: "Analysis result from LRS", key: "analysis_result",
          render: (_, record) => {
            if (!Object.keys(record.geneyx_case).length) return "-";
            return record.geneyx_case["SubStatusName"]
          }
        },
        { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
        { title: "Joint Analysis Status", key: "joint analysis status",
          render: (_, record) => {
            return record.cohort_analysis
          }
        },
        { title: "Gene", key: "gene_of_interest",
          render: (_, record) => {
            const items = Array.isArray(record.genetic_findings) ? record.genetic_findings : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "genetic_findings";
                  const idField = getIdentifier(schemaKey);
                  const label = entry["gene_of_interest"] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "Variant", key: "hgvsc",
          render: (_, record) => {
            const items = Array.isArray(record.genetic_findings) ? record.genetic_findings : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "genetic_findings";
                  const idField = getIdentifier(schemaKey);
                  const label = entry["hgvsc"] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "Notes/other notable findings", key: "case_notes",
          render: (_, record) => {
            const items = Array.isArray(record.geneyx_case_notes) ? record.geneyx_case_notes : [];
            if (!items.length) return "-";

            return (
              <div>
                {items.map((entry, index) => {
                  const parser = new DOMParser();
                  const doc = parser.parseFromString(entry["Note"], "text/html");
                  const note = doc.body.textContent;
                  return note
                })}
              </div>
            );
          }
        },
        { title: "Sex", key: "sex",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.sex || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Race", key: "reported_race",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.reported_race || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Ethnicity", key: "reported_ethnicity",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.reported_ethnicity || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Age", key: "age_at_enrollment",
          render: (_, record) => {
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.age_at_enrollment || "NA"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Phenotype", key: "phenotype_description",
          render: (_, record) => {
            const pheno = record.participant.phenotype_description;
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { pheno || "NA" }
                  </Button>
              </div>
            )
          }
        },
        { title: "Prior Testing", key: "prior_testing",
          render: (_, record) => {
            const prior_testing = record.participant.prior_testing;
            return (
              <div className="action-btn">
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { prior_testing || "NA" }
                  </Button>
              </div>
            )
          }
        },
        { title: "PacBio Alignments", key: "pac_bio_alignments",
          render: (_, record) => {
            const items = Array.isArray(record.aligned_pac_bio) ? record.aligned_pac_bio : [];
            if (!items.length) return "✕";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "aligned_pac_bio";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "Nanopore Alignments", key: "nanopore_alignments",
          render: (_, record) => {
            const items = Array.isArray(record.aligned_nanopore) ? record.aligned_nanopore : [];
            if (!items.length) return "✕";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "aligned_nanopore";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "SR-GS Alignments", key: "sr_gs_alignments",
          render: (_, record) => {
            const items = Array.isArray(record.aligned_dna_short_read) ? record.aligned_dna_short_read : [];
            if (!items.length) return "✕";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "aligned_dna_short_read";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "SR-RNA Alignments", key: "sr_rna_alignments",
          render: (_, record) => {
            const items = Array.isArray(record.aligned_rna_short_read) ? record.aligned_rna_short_read : [];
            if (!items.length) return "✕";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "aligned_rna_short_read";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        },
        { title: "Biobank", key: "biobank",
          render: (_, record) => {
            const items = Array.isArray(record.biobank) ? record.biobank : [];
            if (!items.length) return "✕";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "biobank_entries";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "NA";
                  return (
                    <div className="action-btn">
                      <Button
                        key={index}
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => {handleOpen(schemaKey, entry)}}
                      >{label}</Button>
                    </div>)
                })}
              </div>
            );
          }
        }
      ]}
    />
    </>
  );
}