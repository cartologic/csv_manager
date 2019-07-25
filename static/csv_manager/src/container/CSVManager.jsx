import React, { Component } from 'react'
import MainPage from '../components/MainPage'
import { getCRSFToken } from '../utils'

export default class CSVManager extends Component {
    constructor(props) {
        super(props)
        this.state = {
            csvItems: [],
            publishDialogOpen: false,
            publishDialogData: {
                item: {},
                error: '',
            },
            loading: false,
            listLoading: false,
            uploadLoading: false,
        }
        this.onDrop = this.onDrop.bind(this)
        this.fetchListOfCsvFiles = this.fetchListOfCsvFiles.bind(this)
        this.handlePublishDialogClose = this.handlePublishDialogClose.bind(this)
        this.handlePublishDialogOpen = this.handlePublishDialogOpen.bind(this)
        this.handlePublishDialogPublish = this.handlePublishDialogPublish.bind(this)
        this.handlePublishDialogDelete = this.handlePublishDialogDelete.bind(this)
        this.handleSelectChange = this.handleSelectChange.bind(this)
    }
    handlePublishDialogDelete() {
        this.setState({
            loading: true,
        },
            () => {
                let item = this.state.publishDialogData.item
                let formData = new FormData()
                formData.append('csrfmiddlewaretoken', getCRSFToken())
                formData.append('id', item.id)
                formData.append('_method', 'DELETE')
                fetch('http://localhost/apps/csv_manager/upload/', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                })
                    .then((response) => {
                        if (response.status === 200) {
                            response.json()
                                .then((data) => {
                                    this.handlePublishDialogClose()
                                    this.fetchListOfCsvFiles()
                                })
                        }
                    })
            }
        )
    }
    handlePublishDialogPublish() {
        let item = this.state.publishDialogData.item;
        let re = /^[a-z0-9_]{1,63}$/
        this.setState({
            loading: true,
        }, ()=>{

            if (item.table_name && re.test(item.table_name)) {
                let form = new FormData();
                form.append('id', item.id)
                form.append('lat_field_name', item.lat_field_name)
                form.append('lon_field_name', item.lon_field_name)
                form.append('srs', item.srs)
                form.append('table_name', item.table_name)
                form.append('csrfmiddlewaretoken', getCRSFToken())
                fetch('http://localhost/apps/csv_manager/publish/', {
                    method: 'POST',
                    body: form,
                    credentials: 'same-origin',
                })
                    .then(response => {
                        if (response.status === 500) {
                            response.json()
                                .then((error) => {
                                    this.setState({
                                        publishDialogData: {
                                            ...this.state.publishDialogData,
                                            error: error.message,
                                        },
                                        loading: false
                                    })
                                })
                        } else {
                            response.json()
                                .then(response => {
                                    if (response.status) {
                                        this.setState({
                                            publishDialogData: {
                                                ...this.state.publishDialogData,
                                                error: '',
                                            },
                                            loading: false
                                        }, () => { this.fetchListOfCsvFiles() })
                                    }
                                })
                        }
                    })
    
            } else {
                this.setState({
                    publishDialogData: {
                        ...this.state.publishDialogData,
                        error: "Invalid table name! Must be Alphanumeric Ex: table_name_1, Max length: 63 character",
                    },
                    loading: false,
                })
            }
        })
    }
    handlePublishDialogClose() {
        this.setState({
            publishDialogOpen: false,
            loading: false,
            publishDialogData: {
                ...this.state.publishDialogData,
                error: ''
            }
        })
    }
    handlePublishDialogOpen(id) {
        let publishDialogData = {
            ...this.state.publishDialogData,
            item: this.state.csvItems.find((i) => i.id === id)
        }
        this.setState({ publishDialogOpen: true, publishDialogData })
    }
    handleSelectChange(event) {
        let data = this.state.publishDialogData
        let item = data.item
        item = {
            ...item,
            [event.target.name]: event.target.value,
        }
        data = {
            ...data,
            item: item
        }
        this.setState({ publishDialogData: data })
    }
    fetchListOfCsvFiles() {
        this.setState({
            listLoading: true,
        })
        fetch('http://localhost/apps/csv_manager/api/v1/csv_upload/', {
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => this.setState({ listLoading: false, csvItems: data.objects }))
    }
    onDrop(accepted, rejected) {
        for (let i=0; i < accepted.length; i++) {
            this.setState({
                uploadLoading: true,
            }, ()=>{
                let formData = new FormData();
                formData.append('csv_file', accepted[i])
                formData.append('csrfmiddlewaretoken', getCRSFToken())
                fetch('http://localhost/apps/csv_manager/upload/', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                })
                    .then(response => response.json())
                    .then(response => {
                        if (response.status) {
                            this.setState({uploadLoading: false}, ()=>{this.fetchListOfCsvFiles()})
                        }
                    })
            })
        }
    }
    componentDidMount() {
        this.fetchListOfCsvFiles()
    }
    render() {
        const props = {
            onDrop: this.onDrop,
            handlePublishDialogClose: this.handlePublishDialogClose,
            handlePublishDialogOpen: this.handlePublishDialogOpen,
            handlePublishDialogPublish: this.handlePublishDialogPublish,
            handlePublishDialogDelete: this.handlePublishDialogDelete,
            handleSelectChange: this.handleSelectChange,

            uploadLoading: this.state.uploadLoading,
            listLoading: this.state.listLoading,
            loading: this.state.loading,
            csvItems: this.state.csvItems,
            publishDialogOpen: this.state.publishDialogOpen,
            publishDialogData: this.state.publishDialogData,
        }
        return (
            <MainPage {...props} />
        )
    }
}