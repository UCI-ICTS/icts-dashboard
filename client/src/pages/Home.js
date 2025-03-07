import React from "react";
import { Box, Container, Grid } from "@mui/material"
import "../App.css"
import { InfoBox } from "../components/InfoBox";
import { TableForm } from "../components/TableForm";
import { Uploader } from "../components/Uploader";

const HomePage = () => {
    return (
      <Grid className="container-test" >
        <InfoBox
          header="UCI Institute for Clinical & Translational Science"
          bodyText={
            "The UC Irvine Institute for Clinical and Translational Science (ICTS) is funded"
            + " by the National Institutes of Health (NIH) under the Clinical and Translational"
            + " Sciences Award (CTSA) program. Currently, there are more than 50 medical"
            + " research institutions throughout the United States that receive CTSA"
            + " program funding.The ICTS functions as a local centerpiece for the national"
            + " program, and is dedicated to advancing scientific discovery and medical"
            + " breakthroughs. Collectively, our goal is simple: to accelerate these"
            + " discoveries from the lab and translate them into life-altering medical care."
          }
          linkTo={"https://icts.uci.edu/"}
        />
      </Grid>
    )
}

export default HomePage;