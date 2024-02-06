
import { useDispatch, useSelector } from 'react-redux';
import CSVReader from 'react-csv-reader'
import { setJsonData, submitParticipant } from '../../slices/dataSlice';
import { TableForm } from './TableForm';

export const Uploader = () => {
  const dispatch = useDispatch();
  const tableData = useSelector(state => state.data['jsonData'])
  const handleCsvUpload = (sheet) => {
    dispatch(setJsonData(sheet));
  };

  return (
    <div>
      <CSVReader onFileLoaded={handleCsvUpload}/>
      <div>
        {
          (tableData !== null) ? (
            <TableForm /> 
          ) : (
            <div>test</div>
          )
        }
      </div>
    </div>
  );
};
