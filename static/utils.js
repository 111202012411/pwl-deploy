export function parse_numbers(value) {

    // TODOS: parse number into Date
    
    // passing number
    if (typeof value == "number") return value
    
    // if value as string
    if (typeof value == "string") {

        // normalize string
        value = value.trim()

        let check_dot = value.includes(".")
        let check_comma = value.includes(",")
        let check_float = value.endsWith("f")
        let check_bigint = value.endsWith("n")
        let check_extra = check_dot ||
                    check_comma ||
                    check_float ||
                    check_bigint
        let index_dot = value.lastIndexOf(".")
        let index_comma = value.lastIndexOf(",")
        let last_index_dot = index_dot

        // extra, if context includes dollar symbol character
        if (value.startsWith("$")) value = value.substring(1, value.length).trim()

        // check dot (Float), comma (Currency), n (BigInt), f (Float)
        if (check_extra) {

            if (check_comma) {

                if (check_dot) {

                    // check last index
                    if (index_comma < index_dot) {

                        // replace all commas into empty string
                        value = value.replace(/\,/g, "")

                    } else {

                        // replace all dots into empty string
                        value = value.replace(/\./g, "")
                        
                        // single processing
                        // change comma into dot
                        let temp = Array.from(value)
                        temp.splice(index_comma, 1, ".")
                        last_index_dot = index_comma

                        // store back
                        value = temp.join("")
                    }

                } else {

                    // replace all commas into dot
                    value = value.replace(/\,/g, ".")
                }

                // update check
                check_comma = false
                check_dot = true
            }

            // check dot in context is just once
            if (value.indexOf(".") == last_index_dot) {

                // passing
            
            } else {

                // bypass
                // make single dot in context
                // value = value.slice(0, last_index_dot - 1) + value.slice(last_index_dot)
                let temp = value.split(".")
                let j = temp.length - 1

                // clear value
                value = ""

                // skip entire dots
                for (let i = 0; i < j; i++) {

                    value += temp[i]
                }

                // fix this issue
                // problem with currency
                let w = temp[j]

                // keep last dot
                value += w.length < 3 ?  "." + w : w

            }

            // if Float
            if (check_float || check_dot) {

                if (check_float) value = value.substring(0, value.length - 1)
                let a = Number.parseFloat(value)

                if (0 < a) return a
            }

            // if BigInt
            if (check_bigint) {

                // delete 'n' last character
                value = value.substring(0, value.length - 1)

                return BigInt(value)
            }
            
        } else {

            let a = Number.parseInt(value)

            if (0 < a) return a 
        }
    }

    return 0
}

/*
* @param {String} value
* @return {String}
*/
export function last_modified_to_str(context) {

    let a = new Date
    let b = new Date(context)

    let years = a.getYear() - b.getYear()
    let month = a.getMonth() - b.getMonth()
    let days = a.getDay() - b.getDay()
    let hours = a.getHours() - b.getHours()
    let minutes = a.getMinutes() - b.getMinutes()
    let seconds = a.getSeconds() - b.getSeconds()

    if (years) return years + "year" + (years > 1 ? "s " : " ") + "ago"
    if (month) return month + "month ago"
    if (days) return days + "day" + (days > 1 ? "s " : " ") + "ago"
    if (hours) return hours + "h ago"
    if (minutes) return minutes + "m ago"
    if (seconds) return seconds + "s ago"
    return "new"
}

export function parse_url_search(search) {

    if (search instanceof URL) search = search.search
    if (!search.startsWith("?")) return []

    let urlSearchParams = new URLSearchParams(search)

    let data = {}

    for (let [k, v] of urlSearchParams.entries()) {

        if (k in data) {

            if (Array.isArray(data[k])) {

                data[k].push(v);
            
            } else {

                data[k] = [ data[k], v ]

            }
        } else {

            // magic numbers
            let try_parse_numbers = parse_numbers(v)
            let w = v == "0" ? 0 : v

            data[k] = try_parse_numbers > 0 ? try_parse_numbers : w
        }
    }

    return data
}

export function noctx(e) {

    e.preventDefault()
    e.stopPropagation()
}

export function map_to_dict(map) {

    let check = map instanceof Map || map instanceof FormData
    if (!check) return null

    let data = {}

    for (let [k, v] of map.entries()) {

        // normalize
        if (typeof v === "string") v = v.trim()

        // auto append
        if (k in data) {

            let t = data[k]
            
            if (t instanceof Array) {

                data[k].push(v)
            
            } else {

                data[k] = [ t, v ]
            }

        } else {

            data[k] = v
        }
    }

    return data
}
