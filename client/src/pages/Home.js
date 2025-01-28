import React from "react";
import { Box, Container, Grid } from "@material-ui/core";
import "../App.css"
import { InfoBox } from "../components/InfoBox";
import { TableForm } from "../components/TableForm";
import { Uploader } from "../components/Uploader";

const HomePage = () => {
    return (
      <Container className="container-test" >
        <InfoBox
          header="Some test Text"
          bodyText={"this is a test box. It is waiting for real content. Click me 3 times to go home"}
          linkTo={"/"}
        />
      </Container>
    )
}

export default HomePage;