
import { useDispatch } from 'react-redux';
import CSVReader from 'react-csv-reader'
import { setJsonData, submitParticipant } from '../../slices/dataSlice';
import { Button } from '@material-ui/core';

export const Uploader = () => {
  const dispatch = useDispatch();
  
  const handleCsvUpload = (sheet) => {
      //   dispatch(setJsonData(data));
      const data = convertToJSON(sheet);
      dispatch(submitParticipant({data}));
      console.log("dispatch", data)
  };
  
  const convertToJSON = (sheet) => {
    const data_list = [];
    const header = sheet[0];
    for (let i = 1; i < sheet.length; i++) {
      const row = sheet[i];
      const line = {};
      header.forEach((item, count) => {
        line[item] = row[count];
      });
      data_list.push(line);
    }
    return data_list;
  };

  return (
    <div>
      <CSVReader onFileLoaded={handleCsvUpload} />
      <div>

      </div>
    </div>
  );
};
