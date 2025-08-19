// src/components/SummaryCard.js

import { Button, Card, Popover } from "antd";
import PropTypes from "prop-types";
import "../App.css";

const SummaryCard = ({ title, items = [], loading=false }) => {
  const info_map = {
    "Proband Solve Status": "Participant table plot of each possible solve status.",
    "Participant Snapshot": "List of participants progressing from enrollment,\nto analyte collection, to experiment processing.",
    "Family Breakdown": "List of family types present and their counts.\nAll families counted have one and only one proband.\n'Other' includes families with no parents but are not proband-only.",
    "Biobank Snapshot": "List of biobank entries (tubes) and their\nprocessing statuses. Includes all aliquots.",
    "Analyte Snapshot": "List of analyte specimen types. One analyte -> one experiment.",
    "Genetic Findings Snapshot": "Lists of findings and the distribution of phenotype contributions. Note that not all findings counted lead to solves.",
    "Sequencing Experiments": "Breakdown of experiment types by platform.",
    "Aligned Experiments": "Breakdown of alignment types by platform.",
    "Sequencing vs Alignment Counts": "Compare how many experiments made it to sequencing. Flag any experiments that did not make it to sequencing and are not 'QC Fail'",
    "undefined": "The table is undefined",
  }
  console.log(title, info_map[title])

  return (
    <Card title={<span className="card-title">{title}</span>} className="primary-card">
      {loading ? (
        <p>Loading....</p>
      ) : (
        items.map(({ label, value, key, icon, indent }) => (
          <p key={key || label} style={indent ? { paddingLeft: 16 } : {}}>
            {icon && <span style={{ marginRight: 6 }}>{icon}</span>}
            <span className="card-label">{label}:&nbsp;&nbsp;</span>
            <span className="card-number">{value}</span>
          </p>
        ))
      )
    }
    </Card>
  );
};

SummaryCard.propTypes = {
  title: PropTypes.string.isRequired,
  items: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.node]),
      key: PropTypes.string,
      icon: PropTypes.node,
      indent: PropTypes.bool,
      hoverable: PropTypes.bool,
    })
  ),
};

export default SummaryCard;
