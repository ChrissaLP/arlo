import React from 'react'
import styled from 'styled-components'
import { H1, RadioGroup, Radio, Button } from '@blueprintjs/core'
import { Formik, FormikProps, Form, Field, getIn } from 'formik'
import FormWrapper from '../Form/FormWrapper'
import FormSection from '../Form/FormSection'
import { AuditMember } from '../../types'

const LabelText = styled.span`
  display: block;
  margin: 5px 0;
`

const NameField = styled(Field)`
  margin-bottom: 20px;
`

interface Props {
  setIsLoading: (arg0: boolean) => void
  isLoading: boolean
  setDummy: (arg0: number) => void
  boardName: string
  jurisdictionName: string
}

const MemberForm: React.FC<Props> = ({
  boardName,
  jurisdictionName,
  setDummy,
}: Props) => {
  return (
    <>
      <H1>Member Sign in for Audit Board: {boardName}</H1>
      <p>
        Enter the information below for each member of {jurisdictionName}{' '}
        {boardName} below, then click "Next" to proceed.
      </p>
      <FormWrapper>
        <Formik
          initialValues={[
            {
              name: '',
              affiliation: '',
            },
            {
              name: '',
              affiliation: '',
            },
          ]}
          onSubmit={values => {
            console.log(values)
            setDummy(1)
          }}
          render={({
            setFieldValue,
            values,
          }: FormikProps<[AuditMember, AuditMember]>) => (
            <Form>
              {[0, 1].map(i => (
                <FormSection label="Audit Board Member" key={i}>
                  <label>
                    <LabelText>Full Name</LabelText>
                    <NameField name={`[${i}]name`} />
                  </label>
                  <label>
                    <LabelText>
                      Party Affiliation <i>(optional)</i>
                    </LabelText>
                    <RadioGroup
                      name={`[${i}]affiliation`}
                      onChange={e =>
                        setFieldValue(
                          `[${i}]affiliation`,
                          e.currentTarget.value
                        )
                      }
                      selectedValue={getIn(values, `[${i}]affiliation`)}
                    >
                      <Radio value="DEM">Democrat</Radio>
                      <Radio value="REP">Republican</Radio>
                      <Radio value="LIB">Libertarian</Radio>
                      <Radio value="IND">Independent/Unaffiliated</Radio>
                      <Radio value="">None</Radio>
                    </RadioGroup>
                  </label>
                </FormSection>
              ))}
              <Button intent="primary" type="submit">
                Next
              </Button>
            </Form>
          )}
        />
      </FormWrapper>
    </>
  )
}

export default MemberForm