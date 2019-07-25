import React, { Component } from 'react'
import AppBar from '../components/AppBar'
import ContentWrapper from '../components/ContentWrapper'

export default (props) => (
    <div className='page-wrapper'>
        <AppBar {...props} />
        <ContentWrapper {...props} />
    </div>
)