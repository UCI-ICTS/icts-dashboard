// src/components/SummaryCard.js

import { Card } from "antd";
import PropTypes from "prop-types";
import "../App.css";

const SummaryCard = ({ title, items = [], loading=false }) => {
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
    })
  ),
};

export default SummaryCard;
