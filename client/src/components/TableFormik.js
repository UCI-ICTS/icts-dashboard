import React from 'react';
import { useDispatch } from 'react-redux';
import { Formik, Field, Form, FieldArray, ErrorMessage } from 'formik';
import { useSelector } from 'react-redux';
import { submitParticipant } from '../slices/dataSlice';

export const TableForm = () => {
  const dispatch = useDispatch();
  const thing = useSelector(state => state.data)
  const tableView = useSelector(state => state.data.tableView);
  const tableData = useSelector(state => state.data[tableView]);
  const initialValues = { rows: tableData };
  const table_head = ['participant_id', 'internal_project_id', 'gregor_center', 'consent_code', 'recontactable', 'pmid_id', 'family_id', 'paternal_id', 'maternal_id', 'twin_id', 'proband_relationship', 'proband_relationship_detail', 'sex', 'sex_detail', 'reported_race', 'reported_ethnicity', 'ancestry_detail', 'age_at_last_observation', 'affected_status', 'phenotype_description', 'age_at_enrollment', 'prior_testing', 'case_level_result', 'updated_at', 'phenotype_id', 'solve_status', 'missing_variant_case', 'missing_variant_details']
  console.log(tableView, thing, tableData)
  
  const convertToJSON = (data) => {
    const data_list = [];
    const actualHeaders = data[0];
    const participant_valid = table_head.every(header => actualHeaders.includes(header));
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      const line = {};
      actualHeaders.forEach((item, count) => {
        line[item] = row[count];
      });
      data_list.push(line);
    }
    return [data_list, participant_valid];
  }

    const handleSubmit = (values) => {
      const [data_list, data_type] = convertToJSON(values.rows)
      if (data_type === true) {
        dispatch(submitParticipant({data_list}))
        console.log(data_list)
      }
    };

    if (!tableData || tableData.length === 0) {
      return <div>Loading...</div>;
    }

  return (
    <Formik initialValues={initialValues} onSubmit={handleSubmit}>
      {({ values }) => (
        <Form>
          <FieldArray
            name="rows"
            render={arrayHelpers => (
              <div>
                <button
                  type="button"
                  onClick={() => arrayHelpers.push({})}
                >
                  Add Row
                </button>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(table_head).map(key => (
                          <th key={key}>{table_head[key]}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {values.rows.map((row, index) => (
                        (index >= 0) ? (
                        <tr key={index}>
                          {Object.keys(row).length > 0 ? Object.keys(row).map(key => (
                            <td key={`${key}-${index}`}>
                              <Field name={`rows[${index}].${key}`} value={row[key] || ""} />
                              <ErrorMessage name={`rows[${index}].${key}`} component="div" />
                            </td>
                          )) : (
                            <></>
                          )}
                          <td>
                            <button
                              type="button"
                              onClick={() => arrayHelpers.remove(index)} // Remove this row
                            >
                              Remove
                            </button>
                          </td>
                        </tr>) : (<></>)
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          />
          <button type="submit">Submit</button>
        </Form>
      )}
    </Formik>
  );
};
