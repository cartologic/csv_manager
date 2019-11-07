export const getCRSFToken = () => {
    let csrfToken, csrfMatch = document.cookie.match( /csrftoken=(\w+)/ )
    if ( csrfMatch && csrfMatch.length > 0 ) {
        csrfToken = csrfMatch[ 1 ]
    }
    return csrfToken
};

export const validateFieldName = (fieldName) => {
    return fieldName && fieldName.length > 0
}

export const validateTableName = (tableName) => {
    let re = /^[a-z0-9_]{1,63}$/
    return tableName && re.test(tableName)
}