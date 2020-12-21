import React, { Component } from 'react'
import MainPage from '../components/MainPage'
import { getCRSFToken, validateFieldName, validateTableName } from '../utils'

export default class CSVManager extends Component {
    constructor(props) {
        super(props)
        this.state = {
            csvItems: [],
            publishDialogOpen: false,
            publishDialogData: {
                item: {},
                error: '',
                formErrors: undefined,
                layerURL: undefined,
            },
            loading: false,
            listLoading: false,
            uploadLoading: false,
            nextUrl: false,
            prevUrl: false,
            limit: 20,
            offset: 0,
            total: 0,
        }
        // globalURLS are predefined in index.html otherwise use the following defaults
        this.urls = globalURLS
        this.onDrop = this.onDrop.bind(this)
        this.validateXYFormData = this.validateXYFormData.bind(this)
        this.validateWKTFormData = this.validateWKTFormData.bind(this)
        this.fetchListOfCsvFiles = this.fetchListOfCsvFiles.bind(this)
        this.handlePublishDialogClose = this.handlePublishDialogClose.bind(this)
        this.handlePublishDialogOpen = this.handlePublishDialogOpen.bind(this)
        this.handlePublishDialogPublish = this.handlePublishDialogPublish.bind(this)
        this.handlePublishDialogDelete = this.handlePublishDialogDelete.bind(this)
        this.handleSelectChange = this.handleSelectChange.bind(this)
        this.paginationProps = this.paginationProps.bind(this)
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
                fetch(this.urls.uploadCSV, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                })
                    .then((response) => {
                        if(response.redirected){
                            const regex = new RegExp('/account/login')
                            if(regex.test(response.url)) window.location = this.urls.baseURL + 'account/login/?next=' + this.urls.baseURL
                            else window.location = response.url
                        }
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
    validateXYFormData(item) {
        let formErrors = undefined
        if (!validateTableName(item.table_name)) {
            formErrors = {
                ...formErrors,
                table_name: true
            }
        }
        if (!validateFieldName(item.lat_field_name)) {
            formErrors = {
                ...formErrors,
                lat_field_name: true
            }
        }
        if (!validateFieldName(item.lon_field_name)) {
            formErrors = {
                ...formErrors,
                lon_field_name: true
            }
        }
        return formErrors
    }
    validateWKTFormData(item) {
        let formErrors = undefined
        if (!validateTableName(item.table_name)) {
            formErrors = {
                ...formErrors,
                table_name: true
            }
        }
        if (!validateFieldName(item.wkt_field_name)) {
            formErrors = {
                ...formErrors,
                wkt_field_name: true
            }
        }
        if (!validateFieldName(item.geometry_type)) {
            formErrors = {
                ...formErrors,
                geometry_type: true
            }
        }
        return formErrors
    }
    handlePublishDialogPublish(wkt = false) {
        let item = this.state.publishDialogData.item;
        let formErrors = wkt ? this.validateWKTFormData(item) : this.validateXYFormData(item)
        const submitXYForm = item => {
            let form = new FormData();
            form.append('id', item.id)
            form.append('lat_field_name', item.lat_field_name)
            form.append('lon_field_name', item.lon_field_name)
            form.append('srs', item.srs)
            form.append('table_name', item.table_name || '')

            form.append('wkt_field_name', '')
            form.append('geometry_type', 'POINTXY')

            form.append('csrfmiddlewaretoken', getCRSFToken())
            return fetch(this.urls.publishCSV, {
                method: 'POST',
                body: form,
                credentials: 'same-origin',
            })
        }
        const submitWKTForm = item => {
            let form = new FormData();
            form.append('id', item.id)
            form.append('lat_field_name', '')
            form.append('lon_field_name', '')
            form.append('srs', item.srs)
            form.append('table_name', item.table_name || '')

            form.append('wkt', true)
            form.append('wkt_field_name', item.wkt_field_name)
            form.append('geometry_type', item.geometry_type)

            form.append('csrfmiddlewaretoken', getCRSFToken())
            return fetch(this.urls.publishCSV, {
                method: 'POST',
                body: form,
                credentials: 'same-origin',
            })
        }
        this.setState({
            loading: true,
        }, () => {
            if (!formErrors) {
                const submitFunction = wkt ? submitWKTForm : submitXYForm
                submitFunction(item)
                .then(response => {
                    if(response.redirected){
                        const regex = new RegExp('/account/login')
                        if(regex.test(response.url)) window.location = this.urls.baseURL + 'account/login/?next=' + this.urls.baseURL
                        else window.location = response.url
                    }
                    if (response.status === 400) {
                        response.json()
                            .then((error) => {
                                this.setState({
                                    publishDialogData: {
                                        ...this.state.publishDialogData,
                                        error: error.error,
                                        formErrors: undefined,
                                        layerURL: undefined,
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
                                            formErrors: undefined,
                                            layerURL: globalURLS.layerDetail(response.layer_name)
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
                        formErrors: formErrors,
                        layerURL: undefined,
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
                error: '',
                formErrors: undefined,
                layerURL: undefined,
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
    fetchListOfCsvFiles(url) {
        if(!url){
            url = new URL(this.urls.csvFilesApi, this.urls.siteURL)
            url.searchParams.set('limit', this.state.limit)
            url.searchParams.set('offset', this.state.offset)
        }
        this.setState({
            listLoading: true,
        })
        fetch(url, {
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => this.setState({ 
                listLoading: false, 
                csvItems: data.objects, 
                nextUrl: data.meta.next, 
                prevUrl: data.meta.previous ,
                limit: data.meta.limit,
                offset: data.meta.offset,
                total: data.meta.total_count,
            }))
    }
    onDrop(accepted, rejected) {
        const removeSpecialCharacters = (str) => {
            return str.replace(/[^A-Z0-9.]+/ig, "_");
        }
        for (let i = 0; i < accepted.length; i++) {
            this.setState({
                uploadLoading: true,
            }, () => {
                let file = new File(
                    [accepted[i]],
                    removeSpecialCharacters(accepted[i].name).toLowerCase(),
                    { type: accepted[i].type, },
                    accepted[i].preview
                );
                let formData = new FormData();
                formData.append('csv_file', file)
                formData.append('csrfmiddlewaretoken', getCRSFToken())
                fetch(this.urls.uploadCSV, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                })
                    .then(response => response.json())
                    .then(response => {
                        if (response.status) {
                            this.setState({ uploadLoading: false }, () => { 
                                this.fetchListOfCsvFiles() 
                            })
                        }
                    })
            })
        }
    }
    componentDidMount() {
        this.fetchListOfCsvFiles()
    }
    paginationProps = ()=>({
        onNext: ()=>{
            if(this.state.nextUrl)
                this.fetchListOfCsvFiles(new URL(this.state.nextUrl, this.urls.siteURL))
        },
        onPrev: ()=>{
            if(this.state.prevUrl)
                this.fetchListOfCsvFiles(new URL(this.state.prevUrl, this.urls.siteURL))
        },
        nextUrl: this.state.nextUrl,
        prevUrl: this.state.prevUrl,
        limit: this.state.limit,
        offset: this.state.offset,
        total: this.state.total,
    })
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

            urls: this.urls,
            paginationProps: this.paginationProps(),
        }
        return (
            <MainPage {...props} />
        )
    }
}