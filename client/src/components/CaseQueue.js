// components/CaseQueue.js

import "../App.css"
import { useState } from "react";
import { Button, Table, Spin } from "antd";
import { useSelector } from "react-redux";
import { getIdentifier } from "../utils/schemaAndTables";

export default function CaseQueue({
  selectedRow,
  setSelectedRow,
  onRow,
  queueLoading,
  setQueueLoading,
  openModal
}) {
  const caseData =  useSelector((state) => state.data.caseQueue)
  const rows = Array.isArray(caseData) ? caseData[0] : []
  const handleOpen = (schemaKey, record) => {
    if (openModal && record) {
      openModal("edit", { schemaKey, record });
    }
  };
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
      >Clear</Button>&nbsp;&nbsp;PacBio Case Queue for: {selectedRow.participant_id}
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
                    { record.participant.participant_id || "✓"}
                  </Button>
              </div>
            )
          }
        },
        { title: "Family Size",
          key: "family size",
          render: (_, record) => {
            return record.family_size
          }
        },
        { title: "Relation", dataIndex: "proband_relationship", key: "proband_relationship" },
        { title: "Joint Analysis Status",
          key: "joint analysis status",
          render: (_, record) => {
            return record.cohort_analysis
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
        { title: "Analytes", key: "analytes",
          render: (_, record) => {
            const items = Array.isArray(record.sequencing) ? record.analytes : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "analytes";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "✓";
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
        { title: "Sequencing", key: "sequencing",
          render: (_, record) => {
            const items = Array.isArray(record.sequencing) ? record.sequencing : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "experiment_pac_bio";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "✓";
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
        { title: "Alignments", key: "alignments",
          render: (_, record) => {
            const items = Array.isArray(record.alignments) ? record.alignments : [];
            if (!items.length) return "-";
            return (
              <div>
                {items.map((entry, index) => {
                  const schemaKey = "aligned_pac_bio";
                  const idField = getIdentifier(schemaKey);
                  const label = entry[idField] ||  "✓";
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
            )
          }
        }
      ]}
    />
    </>
  );
}