import React, { useContext } from 'react'
import {
  BrowserRouter as Router,
  Route,
  RouteProps,
  Switch,
  Redirect,
} from 'react-router-dom'
import './App.css'
import styled from 'styled-components'
import { ToastContainer } from 'react-toastify'
import Header from './components/Header'
import { Wrapper } from './components/Atoms/Wrapper'
import {
  AuditAdminView,
  JurisdictionAdminView,
} from './components/MultiJurisdictionAudit'
import SingleJurisdictionAudit from './components/SingleJurisdictionAudit'
import DataEntry from './components/DataEntry'
import CreateAudit from './components/CreateAudit'
import 'react-toastify/dist/ReactToastify.css'
import AuthDataProvider, { AuthDataContext } from './components/UserContext'
import { IUserMeta } from './types'
import CreateSingleJurisdictionAudit from './CreateSingleJurisdictionAudit'

const Main = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100vh;
`

interface PrivateRouteProps extends RouteProps {
  userType: IUserMeta['type']
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({
  userType,
  ...props
}: PrivateRouteProps) => {
  const { isAuthenticated, meta } = useContext(AuthDataContext)
  if (isAuthenticated === null) {
    // Still loading /auth/me, don't show anything
    return <></>
  }
  if (isAuthenticated && userType === meta!.type) {
    return <Route {...props} />
  }
  return (
    <Route
      render={() => (
        <Redirect
          to={{
            pathname: '/',
            state: { from: props.location },
          }}
        />
      )}
    />
  )
}

const App: React.FC = () => {
  return (
    <Router>
      <ToastContainer />
      <AuthDataProvider>
        <Main>
          <Route path="/" component={Header} />
          <Switch>
            <Route exact path="/" component={CreateAudit} />
            <Route
              exact
              path="/audit"
              component={CreateSingleJurisdictionAudit}
            />
            <Route
              path="/audit/:electionId"
              component={SingleJurisdictionAudit}
            />
            <PrivateRoute
              userType="audit_board"
              path="/election/:electionId/audit-board/:auditBoardId"
              component={DataEntry}
            />
            <PrivateRoute
              userType="jurisdiction_admin"
              path="/election/:electionId/jurisdiction/:jurisdictionId"
              component={JurisdictionAdminView}
            />
            <PrivateRoute
              userType="audit_admin"
              path="/election/:electionId/:view?"
              component={AuditAdminView}
            />
            <Route>
              <Wrapper>404 Not Found</Wrapper>
            </Route>
          </Switch>
        </Main>
      </AuthDataProvider>
    </Router>
  )
}

export default App
