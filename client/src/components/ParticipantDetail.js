// components/ParticipantDetail.js

import "../App.css"
import { useState } from "react";
import { Button, Table, Spin } from "antd";
import { useSelector, useDispatch } from "react-redux";
import { getIdentifier } from "../utils/schemaAndTables";
import { openReport } from "../slices/dataSlice";

export default function ParticipantDetail({
  selectedRow,
  setSelectedRow,
  onRow,
  detailLoading,
  setDetailLoading,
  openModal
}) {
  const dispatch = useDispatch();
  const familyData =  useSelector((state) => state.data.familyDetail)
  const rows = Array.isArray(familyData) ? familyData[0] : []
  const familyName = selectedRow.participant_id

  const handleOpen = (schemaKey, record) => {
    if (openModal && record) {
      openModal("edit", { schemaKey, record });
    }
  };

  const handleOpenReport = (report) => {
    const objectKey = report.file_path.replace("s3://icts-dashboard-analysis-files/", "")
    console.log("Report Click", objectKey)
    console.log(report.file_path)
    dispatch(openReport(objectKey))
      .unwrap()
      .then((link) => {
        window.open(link.url,  "_blank")
      })
  };

  {detailLoading ? (
      <Spin tip="Loading related family data..." style={{ display: "block", textAlign: "center", marginTop: 20 }}>
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
      >Clear</Button>&nbsp;&nbsp;Family Detail for: {familyName}
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
            const needsReview = record?.participant?.needs_review;
            return (
              <div className={needsReview ? "cell-needs-review" : ""}>
                <Button
                    type="link"
                    style={{ padding: 0 }}
                    onClick={() => handleOpen("participants", record.participant)}
                  >
                    { record.participant.participant_id || "✓"}
                  </Button>
              </div>
            )
          }
         },
         { title: "Biobank",
          key: "biobank",
          render: (_, record) => {
            const items = Array.isArray(record.biobank) ? record.biobank : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "biobank_entries";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "✓";
                  const needsReview = entry?.needs_review
                  return (
                    <div className={needsReview ? "cell-needs-review" : ""} key={index}>
                      <Button
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
        { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
        { title: "Phenotypes",
          key: "pheontypes",
          render: (_, record) => {
            const items = Array.isArray(record.phenotypes) ? record.phenotypes : [];
            return items.length ? (
              <div>
                {items.map((entry, index) => {
                  const needsReview = entry?.needs_review;
                  return (
                    <div className={needsReview ? "cell-needs-review" : ""} key={index}>
                      <Button
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => handleOpen("phenotypes", entry)}
                      >{entry.term_id || "✓"}</Button>
                    </div>
                )})}
              </div>
            ) : "-";
          }
         },
        { title: "Genetic Findings", key: "genetic_findings",
          render: (_, record) => {
            const items = Array.isArray(record.genetic_findings) ? record.genetic_findings : [];
            return items.length ? (
              <div>
                {items.map((entry, index) => {
                  const needsReview = entry?.needs_review;
                  return (
                    <div className={needsReview ? "cell-needs-review" : ""} key={index}>
                      <Button
                        type="link"
                        style={{ padding: 0 }}
                        onClick={() => handleOpen("genetic_findings", entry)}
                      >{entry.genetic_findings_id || "✓"}</Button>
                    </div>
                )})}
              </div>
            ) : "-";
          }
        },
        { title: "Sequencing", key: "sequencing",
          render: (_, record) => {
            const items = Array.isArray(record.sequencing) ? record.sequencing : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = entry.table_type;
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "✓";
                  return (
                    <div className="action-btn" key={index}>
                      <Button
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
        { title: "Alignments", key: "alignments",
          render: (_, record) => {
            const items = Array.isArray(record.alignments) ? record.alignments : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = entry.table_type;
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "✓";
                  return (
                    <div className="action-btn" key={index}>
                    <Button
                      type="link"
                      style={{ padding: 0 }}
                      onClick={() => {handleOpen(schemaKey, entry)}}
                    >{label}</Button>
                    </div>)
                })}
              </div>
            )
          }
        },
        { title: "QAQC Reports", key: "reports",
          render: (_, record) => {
            const items = Array.isArray(record.reports) ? record.reports : [];
            console.log(items)
            if (!items.length) return "-";
            return (
              <div>
                {items.map((report, index) => {
                  const label = report.file_name
                  return(
                    <div className="action-btn" key={index}>
                    <Button
                      type="link"
                      style={{ padding: 0 }}
                      onClick={() => {handleOpenReport(report)}}
                    >{label}</Button>
                    </div>
                  )
                })}
              </div>
            )
          }
        },
      ]}
    />
    </>
  );
}