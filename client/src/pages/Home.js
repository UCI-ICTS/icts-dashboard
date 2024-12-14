import React from "react";
import { Box, Container, Grid } from "@material-ui/core";
import "../App.css"
import { InfoBox } from "../components/InfoBox";
import { TableForm } from "../components/TableForm";
import { Uploader } from "../components/Uploader";

const HomePage = () => {
    return (
      <Container >
        {/* <Uploader/> */}
        <Grid item xs={12} sm={12} lg={12} xl={12} >
        We will leverage UCI Health’s expertise in genetics and genetic counseling to support an eConsult network 
            <Container className="home-margintop" maxWidth={false}>
              <Box>
                <Grid container justifyContent="space-around" spacing={3}>
                    <Grid item className="home-grid-item">
                        <InfoBox
                          header={"Are you a primary care provider interested in joining eConsult?"}
                          bodyText={"Please contact econsultsupport@support.testing.com for more information"}
                          linkTo= "/contact"
                        />
                    </Grid>
                    <Grid item className="home-grid-item">
                        <InfoBox
                          header={"PMGRC eConsult Login"}
                          bodyText={"PMGRC signin via OAuth2"}
                          linkTo= "login"
                        />
                    </Grid>
                    <Grid item className="home-grid-item">
                        <InfoBox
                          header={"How to complete and eConsult"}
                          bodyText={"Access our how-to guides here to see how to complete an eConsult"}
                          linkTo= "/forms/refferal"
                        />
                    </Grid>
                    <Grid item className="home-grid-item">
                        <InfoBox
                          header={"GREGoR Data Tables"}
                          bodyText={"Access the GREGoR data tables and dashboard"}
                          linkTo= "/forms/gregor"
                        />
                    </Grid>
                </Grid>
              </Box>
            </Container>
          </Grid>
      </Container>
    )
}

export default HomePage;