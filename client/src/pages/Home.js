import React from "react";
import { Box, Container, Grid } from "@material-ui/core";
import "../App.css"
import { InfoBox } from "../components/InfoBox";
import { TableForm } from "../components/TableForm";
import { Uploader } from "../components/Uploader";

const HomePage = () => {
    return (
      <Container className="container-test" >
            <InfoBox />
        <Grid item xs={12} sm={6} lg={4} xl={12}  className="container-test">
          <Box item xs={12} sm={6} lg={4} xl={1} l className="container-test">
          <Box item xs={12} sm={6} lg={4} xl={1} l className="container-test">
          </Box>
          <Box item xs={12} sm={6} lg={4} xl={1} l className="container-test">
          </Box>
          </Box>
        </Grid>
      </Container>
    )
}

export default HomePage;