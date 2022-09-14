import React, {useState} from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faPause} from '@fortawesome/free-solid-svg-icons'
import {faStop} from '@fortawesome/free-solid-svg-icons'

import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import ButtonGroup from 'react-bootstrap/ButtonGroup';
import Modal from 'react-bootstrap/Modal';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs'
import Badge from 'react-bootstrap/Badge';
import Nav from 'react-bootstrap/Nav';
import ListGroup from 'react-bootstrap/ListGroup';
import ProgressBar from 'react-bootstrap/ProgressBar';
import InputGroup from 'react-bootstrap/InputGroup';
import Table from 'react-bootstrap/Table';
import './App.css';

function App() {


    const [showControl, setShowControl] = useState(false);

    const handleCloseControl = () => setShowControl(false);
    const handleShowControl = () => setShowControl(true);

    const [showAdd, setAdd] = useState(false);

    const handleCloseAdd = () => setAdd(false);
    const handleShowAdd = () => setAdd(true);


    return (
        <div className="App">
            <h1 className="title">Printer App</h1>
            <InputGroup className="search d-flex">
                <input className="form-control mr-2" type="search"
                       placeholder="Search Printers"
                       aria-label="Search"/>
                <Button className="search-button" type="submit">Search</Button>
            </InputGroup>
            <hr/>


            <div className="printer-container">
                <Button>Refresh Printers</Button>
                <Button style={{marginLeft: "1rem"}} onClick={handleShowAdd}>Add Printer</Button>
                <Row xs={2} md={4} className="printer-row g-4">
                    {Array.from({length: 4}).map((_, idx) => (
                        <Col>
                            <Card>
                                <Card.Body>
                                    <Card.Title>Printer {idx}
                                        <Badge pill bg="success" style={{float: "right"}}>
                                            Available
                                        </Badge>
                                    </Card.Title>

                                    <Card.Text>
                                        This is a longer card with supporting text below as a natural
                                        lead-in to additional content. This content is a little bit
                                        longer.
                                    </Card.Text>
                                    <div className="card-buttons">
                                        <Button variant="primary" onClick={handleShowControl}>Open</Button>
                                        <Button variant="secondary">Specs</Button>
                                    </div>

                                </Card.Body>
                            </Card>
                        </Col>
                    ))}
                </Row>
            </div>

            {/*printer modal*/}
            <Modal dialogClassName="modal-90w" show={showControl} onHide={handleCloseControl} backdrop="static"
                   fullscreen centered>
                <Modal.Header closeButton>
                    <Modal.Title>Printer 2 Control Panel</Modal.Title>
                </Modal.Header>


                <Modal.Body>
                    <Tab.Container
                        defaultActiveKey="settings"
                        className="mb-3"
                    >
                        <Row>
                            <Col xs={3}>
                                <Nav variant="pills" className="flex-column">
                                    <Nav.Item>
                                        <Nav.Link eventKey="settings">Settings</Nav.Link>
                                    </Nav.Item>
                                    <Nav.Item>
                                        <Nav.Link eventKey="info">Info</Nav.Link>
                                    </Nav.Item>
                                    <hr/>

                                </Nav>
                                <div style={{
                                    overflowY: "scroll",
                                    padding: "0.5rem",
                                    height: "calc(100vh - 285px)",
                                    maxHeight: "calc(100vh - 285px)"
                                }}>
                                    <Card className="printer-state">
                                        <Card.Header as="h6">Status</Card.Header>

                                        <ListGroup className="list-group-flush">
                                            <ListGroup.Item>
                                                <div>
                                                    Machine State: <b>Printing</b> <br/>
                                                    Time Elapsed: <b>00:04:20</b> <br/>
                                                    Total Time Estimate: <b>01:06:09</b> <br/>
                                                    Layer: <b>1 of 3</b> <br/>
                                                </div>
                                                <ProgressBar animated now={45} label="45%"
                                                             style={{marginTop: "0.5rem"}}/>
                                            </ListGroup.Item>
                                            <ListGroup.Item>
                                                Filename: <b>file.mp4</b> <br/>
                                                Job ID: <b>12341234</b>
                                            </ListGroup.Item>
                                            <ListGroup.Item>
                                                <div>
                                                    Feed / Feed Current: <b>???</b> <br/>
                                                </div>

                                            </ListGroup.Item>
                                            <ListGroup.Item>
                                                <Container style={{
                                                    maxWidth: "100%",
                                                    display: "flex",
                                                    alignItems: "center",
                                                    justifyContent: "center"
                                                }}>
                                                    <ButtonGroup size="lg" className="mb-2">

                                                        <Button>
                                                            Pause
                                                            <FontAwesomeIcon icon={faPause}
                                                                             style={{marginLeft: "0.5rem"}}/>
                                                        </Button>
                                                        <Button variant="danger">
                                                            Cancel
                                                            <FontAwesomeIcon icon={faStop}
                                                                             style={{marginLeft: "0.5rem"}}/>
                                                        </Button>
                                                    </ButtonGroup>
                                                </Container>
                                            </ListGroup.Item>
                                        </ListGroup>

                                    </Card>

                                    <Card className="printer-state">
                                        <Card.Header as="h6">Create New Job</Card.Header>

                                        <ListGroup className="list-group-flush">
                                            <ListGroup.Item>

                                                <Tabs
                                                    defaultActiveKey="upload"
                                                    id="fill-tab-example"
                                                    className="mb-3"
                                                    variant="tabs"
                                                    justify
                                                >
                                                    <Tab eventKey="upload" title="Upload File">
                                                        <Form.Group controlId="formFile" className="mb-3">
                                                            <Form.Label>Upload File</Form.Label>
                                                            <Form.Control type="file"/>
                                                        </Form.Group>
                                                    </Tab>
                                                    <Tab eventKey="existing" title="Local File">
                                                        <Form.Label>Directory Path</Form.Label>
                                                        <InputGroup controlId="localPathChooser">
                                                            <Form.Control placeholder="Local"/>
                                                            <Button variant="secondary">Go</Button>
                                                        </InputGroup>
                                                        <hr/>
                                                        <b>5 results in C:\local</b>
                                                        <ListGroup variant="flush">
                                                            <ListGroup.Item action variant="light">asldkfasdf.gcode</ListGroup.Item>
                                                            <ListGroup.Item action variant="light">asdfkasdfl.gcode</ListGroup.Item>
                                                            <ListGroup.Item action variant="light">asldfsladfdsa.gcode</ListGroup.Item>
                                                            <ListGroup.Item action variant="light">bed.gcode</ListGroup.Item>
                                                        </ListGroup>
                                                    </Tab>
                                                </Tabs>


                                            </ListGroup.Item>
                                            <ListGroup.Item>
                                                <Form.Check
                                                    type="checkbox"
                                                    label="The printer is properly configured and prepared for the new job."
                                                    className="mb-3"
                                                />
                                                <Container style={{
                                                    maxWidth: "100%",
                                                    display: "flex",
                                                    alignItems: "center",
                                                    justifyContent: "center"
                                                }}>
                                                    <div>


                                                        <Button size="lg">
                                                            Start
                                                        </Button>
                                                    </div>

                                                </Container>
                                            </ListGroup.Item>
                                        </ListGroup>

                                    </Card>


                                </div>
                            </Col>
                            <Col xs={9}>
                                <Tab.Content>
                                    <Tab.Pane eventKey="settings" title="Settings">
                                        <Form>
                                            <Row className="mb-2">
                                                <Col xs="7">
                                                    <Card className="modal-card" bg="light">
                                                        <h5>Temperatures</h5>
                                                        <Table bordered>
                                                            <thead>
                                                            <tr>
                                                                <td>
                                                                </td>
                                                                <td>
                                                                    Left Nozzle
                                                                </td>
                                                                <td>Right Nozzle</td>
                                                                <td>Heat Bed</td>
                                                            </tr>
                                                            </thead>
                                                            <tbody>
                                                            <tr>
                                                                <td>
                                                                    Target
                                                                </td>
                                                                <td>
                                                                    <InputGroup controlId="formGridEmail">

                                                                        <Form.Control placeholder="74"/>
                                                                        <InputGroup.Text>°C</InputGroup.Text>
                                                                        <Button variant="secondary">Set</Button>
                                                                    </InputGroup>
                                                                </td>
                                                                <td>
                                                                    <InputGroup controlId="formGridEmail">

                                                                        <Form.Control placeholder="74"/>
                                                                        <InputGroup.Text>°C</InputGroup.Text>
                                                                        <Button variant="secondary">Set</Button>
                                                                    </InputGroup></td>
                                                                <td>
                                                                    <InputGroup controlId="formGridEmail">

                                                                        <Form.Control placeholder="74"/>
                                                                        <InputGroup.Text>°C</InputGroup.Text>
                                                                        <Button variant="secondary">Set</Button>
                                                                    </InputGroup></td>
                                                            </tr>
                                                            <tr>
                                                                <td>Actual</td>
                                                                <td>69°C</td>
                                                                <td>69°C</td>
                                                                <td>69°C</td>

                                                            </tr>
                                                            </tbody>
                                                        </Table>

                                                    </Card>
                                                </Col>
                                                <Col xs="5">
                                                    <Card className="modal-card" bg="light">
                                                        <h5>Flowrate</h5>
                                                        <Row className="mb-3" style={{marginTop: "0.5rem"}}>
                                                            <Col>
                                                                <Form.Group as={Col} controlId="formFlowLeft">
                                                                    <Form.Label>Left Nozzle</Form.Label>
                                                                    <Form.Control placeholder="Set Flowrate"/>
                                                                </Form.Group>
                                                            </Col>
                                                            <Col>
                                                                <Form.Group as={Col} controlId="formFlowRight">
                                                                    <Form.Label>Right Nozzle</Form.Label>
                                                                    <Form.Control placeholder="Set Flowrate"/>
                                                                </Form.Group>
                                                            </Col>

                                                        </Row>
                                                    </Card>
                                                </Col>
                                            </Row>
                                            <Row className="mb-2">
                                                <Col xs="8">
                                                    <Card className="modal-card" bg="light">
                                                        <h5>Axis Control</h5>
                                                        <Row className="mb-3" style={{marginTop: "0.5rem"}}>
                                                            <Form.Group as={Col} controlId="formAxisFeed">
                                                                <Form.Label>Feed</Form.Label>
                                                                <Form.Control placeholder="Set Value"/>
                                                            </Form.Group>

                                                            <Form.Group as={Col} controlId="formAxisX">
                                                                <Form.Label>X</Form.Label>
                                                                <Form.Control placeholder="Set Value"/>
                                                            </Form.Group>

                                                            <Form.Group as={Col} controlId="formAxisY">
                                                                <Form.Label>Y</Form.Label>
                                                                <Form.Control placeholder="Set Value"/>
                                                            </Form.Group>
                                                            <Form.Group as={Col} controlId="formAxisZ">
                                                                <Form.Label>Z</Form.Label>
                                                                <Form.Control placeholder="Set Value"/>
                                                            </Form.Group>

                                                            <Form.Group as={Col} controlId="formAxisNozzle">
                                                                <Form.Label>Nozzle</Form.Label>

                                                                <Form.Select aria-label="Default select example">
                                                                    <option>Select</option>
                                                                    <option value="1">Left</option>
                                                                    <option value="2">Right</option>
                                                                </Form.Select>

                                                            </Form.Group>
                                                            <Form.Group as={Col} controlId="formAxisNozzle">
                                                                <Form.Label style={{opacity: "0"}}>.</Form.Label>

                                                                <Form.Control>
                                                                </Form.Control>

                                                            </Form.Group>
                                                        </Row>

                                                    </Card>
                                                </Col>
                                                <Col xs="4">
                                                    <Card className="modal-card" bg="light">
                                                        <h5>Fan</h5>
                                                        <Table bordered size="sm" style={{whiteSpace: "nowrap"}}>
                                                            <thead>
                                                            <tr>
                                                                <td>
                                                                </td>
                                                                <td>
                                                                    Target
                                                                </td>
                                                                <td>Actual</td>
                                                            </tr>
                                                            </thead>
                                                            <tbody>
                                                            <tr>
                                                                <td>
                                                                    Fan Speed
                                                                </td>
                                                                <td>
                                                                    <InputGroup className="w-"
                                                                                controlId="formGridEmail">

                                                                        <Form.Control placeholder="1400"/>
                                                                        <InputGroup.Text>RPM</InputGroup.Text>
                                                                        <Button variant="secondary">Set</Button>
                                                                    </InputGroup>
                                                                </td>
                                                                <td>
                                                                    6900 RPM
                                                                </td>

                                                            </tr>

                                                            </tbody>
                                                        </Table>
                                                    </Card>
                                                </Col>
                                            </Row>

                                        </Form>
                                    </Tab.Pane>
                                    <Tab.Pane eventKey="info" title="Info">
                                        <Card className="printer-state">
                                            <Card.Header as="h6">Device Information</Card.Header>

                                            <ListGroup className="list-group-flush">

                                                <ListGroup.Item>
                                                    Serial No.: <b>A1B2C3D4E5F6G7H</b> <br/>
                                                    Api Ver.: <b>6.9.420</b> <br/>
                                                    Battery: <b>95%</b> <br/>
                                                    Brightness: <b>1 million nits</b> <br/>
                                                    Local Timestamp: <b>11:33 AM UTC 9/1/2022</b> <br/>
                                                    Firmware Ver: <b>6.9.420</b> <br/>
                                                    Language: <b>EN</b> <br/>
                                                    ID: <b>A1B2C3D4E5F6G7H</b> <br/>
                                                    IP: <b>192.168.1.1</b> <br/>
                                                    Name: <b>Joseph</b> <br/>
                                                    Model: <b>S</b> <br/>
                                                    Nozzle Ct.: <b>2</b> <br/>
                                                    Storage Avail.: <b>3GB</b> <br/>
                                                    Update: <b>False</b> <br/>
                                                    Ver.: <b>10000</b>
                                                </ListGroup.Item>
                                            </ListGroup>
                                        </Card>
                                    </Tab.Pane>
                                </Tab.Content>

                            </Col>

                        </Row>
                    </Tab.Container>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleCloseControl}>
                        Close
                    </Button>
                    <Button variant="primary" onClick={handleCloseControl}>
                        Apply Changes
                    </Button>
                </Modal.Footer>
            </Modal>
            {/*add printer modal*/}

            <Modal
                show={showAdd}
                onHide={handleCloseAdd}
                size="lg"
                aria-labelledby="contained-modal-title-vcenter"
                centered
            >
                <Modal.Header closeButton>
                    <Modal.Title id="contained-modal-title-vcenter">
                        Add Printer
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <h4>Instructions</h4>
                    <ol>
                        <li>Turn on secure passcode, set passcode to default value (ask Peng if unsure)</li>
                        <li>Enable static IP in printer settings</li>
                        <li>Enable SSH in printer settings, set passcode to default value as well</li>
                        <li>Enable API in printer settings</li>
                        <li>Input IP address and password below</li>
                    </ol>
                    <Form>
                        <Row>
                            <Col xs={6}>
                    <Form.Group className="mb-3" controlId="formBasicEmail">
                        <Form.Label>IP Address</Form.Label>
                        <Form.Control placeholder="Enter IP Address" />
                    </Form.Group>
                            </Col>
                            <Col xs={6}>
                    <Form.Group className="mb-3" controlId="formBasicPassword">
                        <Form.Label>Password</Form.Label>
                        <Form.Control type="password" placeholder="Password" />
                    </Form.Group>

                            </Col>
                        </Row>

                </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleCloseAdd}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleCloseAdd}>
                        Add Printer
                    </Button>
                </Modal.Footer>
            </Modal>

        </div>
    );
}

export default App;
