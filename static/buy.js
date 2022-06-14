(async global => {

    let { parse_numbers, parse_url_search, last_modified_to_str, noctx, map_to_dict } = await import("/utils.js")

    async function main(e) {

        // no ctx yesss
        document.body.addEventListener("contextmenu", noctx)

        // parse url search
        let params = parse_url_search(location.search)

        let product_id = params?.product_id || 0
        let username = localStorage.getItem("user") || ""

        // get first item from array
        if (Array.isArray(product_id)) product_id = product_id[0]

        // get product from server
        let response = await fetch(location.origin + "/v1/products/get", {

            method: "POST",
            body: JSON.stringify({

                product_id: params?.product_id || 0
            })
        })

        // parse into json
        let data = await response.json()

        let status_code = data?.status_code || 400
        if (status_code === 200) {

            let contents = data?.contents || []

            if (contents.length > 0) {

                let content = contents.shift()

                // "id": 5,
                // "name": "jessie free",
                // "photo": null,
                // "description": "jessie module for free",
                // "categories": "software,module,markup_language,free",
                // "period_of_time": "lifetime",
                // "license": "",
                // "author": "ahmad asy syafiq",
                // "vendor": "unknown",
                // "price": 0.0,
                // "sale": 0.0,
                // "created": "2022-05-31T08:17:41Z",
                // "modified": "2022-05-31T08:17:41Z"

                let product_name = content?.name || "unknown"
                let product_photo = content?.photo || "unknown"
                let product_desc = content?.description || "unknown"
                let product_cat = content?.categories || "unknown"
                let product_period = content?.period_of_time || "unknown"
                let product_license = content?.license || "unknown"
                let product_author = content?.author || "unknown"
                let product_vendor = content?.vendor || "unknown"
                let product_price = content?.price || "0"
                let product_sale = content?.sale || "0"
                let product_created_at = content?.created || "unknown"
                let product_modified_at = content?.modified || "unknown"

                // apply the product into preview
                let productNameEl = document.querySelector("div.product-name")
                let productPhotoEl = document.querySelector("div.product-photo")
                let productDescEl = document.querySelector("div.product-description")
                let productCatEl = document.querySelector("div.product-categories")
                let productPeriodEl = document.querySelector("div.product-period")
                let productLicenseEl = document.querySelector("div.product-license")
                let productAuthorEl = document.querySelector("div.product-author")
                let productVendorEl = document.querySelector("div.product-vendor")
                let productPriceEl = document.querySelector("div.product-price")
                let productSaleEl = document.querySelector("div.product-sale")
                let productCreatedAtEl = document.querySelector("div.product-created")
                let productModifiedAtEl = document.querySelector("div.product-modified")

                if (productNameEl) productNameEl = productNameEl.querySelector("h3.out")
                if (productPhotoEl) productPhotoEl = productPhotoEl.querySelector("img.out")
                if (productDescEl) productDescEl = productDescEl.querySelector("p.out")
                if (productCatEl) productCatEl = productCatEl.querySelector("span.out")
                if (productPeriodEl) productPeriodEl = productPeriodEl.querySelector("span.out")
                if (productLicenseEl) productLicenseEl = productLicenseEl.querySelector("span.out")
                if (productAuthorEl) productAuthorEl = productAuthorEl.querySelector("span.out")
                if (productVendorEl) productVendorEl = productVendorEl.querySelector("span.out")
                if (productPriceEl) productPriceEl = productPriceEl.querySelector("span.out")
                if (productSaleEl) productSaleEl = productSaleEl.querySelector("span.out")
                if (productCreatedAtEl) productCreatedAtEl = productCreatedAtEl.querySelector("span.out")
                if (productModifiedAtEl) productModifiedAtEl = productModifiedAtEl.querySelector("span.out")

                let formatter = new Intl.NumberFormat("ru-RU", {
                    style: "currency",
                    currency: "RUB"
                })

                // make short name, fit in element space
                if (product_author.length > 13)
                    if (product_author.includes(" ")) product_author = product_author.split(" ")[0]

                if (productNameEl) productNameEl.textContent = product_name
                if (productDescEl) productDescEl.textContent = product_desc
                if (productPriceEl) productPriceEl.textContent = formatter.format(parse_numbers(product_price))
                if (productSaleEl) productSaleEl.textContent = formatter.format(parse_numbers(product_sale))
                if (productCreatedAtEl) productCreatedAtEl.textContent = last_modified_to_str(product_created_at)
                if (productModifiedAtEl) productModifiedAtEl.textContent = last_modified_to_str(product_modified_at)

                if (productPhotoEl && product_photo !== "unknown") {

                    if (productPhotoEl instanceof HTMLImageElement) {

                        // photo > image
                        // productPhotoEl.src = "https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg"
                        productPhotoEl.src = product_photo
                    }
                }

                if (product_cat.includes(",")) {

                    let tagName = productCatEl?.tagName || "span"

                    product_cat = product_cat.split(",").map(context => {

                        let spanEl = document.createElement(tagName)
                        spanEl.classList.add("out")
                        spanEl.textContent = context
                        return spanEl
                    })

                    if (productCatEl) {

                        productCatEl.parentElement.append(...product_cat)
                        productCatEl.remove()
                    }                    

                } else {

                    if (productCatEl) productCatEl.textContent = product_cat
                }

                if (productPeriodEl) productPeriodEl.textContent = product_period
                if (productLicenseEl) productLicenseEl.textContent = product_license
                if (productAuthorEl) productAuthorEl.textContent = product_author
                if (productVendorEl) productVendorEl.textContent = product_vendor

                // User Registration Form
                // username: str
                // name: str
                // gender: str
                // day_of_birthday: str
                // email: str
                // phone: str
                // address: str
                // country: str
                // language: str
                // pos_code: str

                // location.origin + "/v1/users/registry"
                let userRegistrationForm = document.querySelector("form#userRegistrationForm")
                let userLoginForm = document.querySelector("form#userLoginForm")
                let transactionForm = document.querySelector("form#transactionForm")

                // let username = userRegistrationForm.querySelector("input#userName")
                // let name = userRegistrationForm.querySelector("input#realName")
                // let gender_male = userRegistrationForm.querySelector("input#genderMale")
                // let gender_female = userRegistrationForm.querySelector("input#genderFemale")
                // let day_of_birthday = userRegistrationForm.querySelector("input#dayOfBirthday")
                // let email = userRegistrationForm.querySelector("input#email")
                // let phone = userRegistrationForm.querySelector("input#phone")
                // let address = userRegistrationForm.querySelector("input#address")
                // let country = userRegistrationForm.querySelector("input#country")
                // let language = userRegistrationForm.querySelector("input#language")
                // let postal_code = userRegistrationForm.querySelector("input#pos_code")
                // let password = userRegistrationForm.querySelector("input#password")
                // let password_confirm = userRegistrationForm.querySelector("input#password_confirm")
                let login = userRegistrationForm.querySelector("button#login")

                if (login) login.addEventListener("click", async (ev) => {

                    let target = ev && ev.target

                    if (target) {

                        userRegistrationForm.parentElement.classList.add("none")
                        userLoginForm.parentElement.classList.remove("none")
                    }
                })

                let user_id = Number.parseInt(localStorage.getItem("id")) || 0
                user_id = Number.isFinite(user_id) ? user_id : 0
                user_id = Number.isNaN(user_id) ? 0 : user_id

                if (username && user_id) {

                    userRegistrationForm.parentElement.classList.add("none")
                    userLoginForm.parentElement.classList.add("none")

                    let w = userLoginForm.parentElement
                    let g = w?.parentElement
                    g.style.display = "none"
                }

                if (userRegistrationForm) userRegistrationForm.addEventListener("submit", async (ev) => {

                    let target = ev && ev?.target

                    if (target) {

                        ev.preventDefault()

                        let dataForm = new FormData(target)

                        let data = map_to_dict(dataForm)

                        let dataIncluded = {}
                        // username
                        dataIncluded.username = data?.username || null
                        // name
                        dataIncluded.name = data?.name || null
                        // gender
                        dataIncluded.gender = data?.gender || null
                        // day_of_birthday
                        dataIncluded.day_of_birthday = data?.day_of_birthday || null
                        // email
                        dataIncluded.email = data?.email || null
                        // phone
                        dataIncluded.phone = data?.phone || null
                        // address
                        dataIncluded.address = data?.address || null
                        // country
                        dataIncluded.country = data?.country || null
                        // language
                        dataIncluded.language = data?.language || null
                        // pos_code
                        dataIncluded.pos_code = data?.pos_code || null
                        // password
                        dataIncluded.password = data?.password || null
                        
                        // check password_confirm
                        if (dataIncluded.password !== data.password_confirm || dataIncluded.password.length === 0) {

                            alert("Password dan konfirmasi password tidak sama! coba ulangi lagi")
                            throw new Error("Password and confirm password does not match!")
                        }

                        let response = await fetch(location.origin + "/v1/users/registry", {

                            method: "POST",
                            body: JSON.stringify(dataIncluded),
                            headers: { "Content-Type": "application/json" }
                        })

                        data = await response.json()

                        if (data.status_code !== 200) {

                            alert(data.message)
                            throw new Error(data.message)
                        
                        } else {

                            alert("User telah ter Registrasi!")
                        }
                        
                        let contents = data?.contents || []

                        if (contents.length > 0) {

                            let content = contents[0]
                            user_id = content?.user_id || 0
                            username = dataIncluded?.username || null
                        }
                    }
                })

                if (userLoginForm) userLoginForm.addEventListener("submit", async (ev) => {

                    let target = ev && ev?.target

                    if (target) {

                        ev.preventDefault()

                        let dataForm = new FormData(target)
                        let data = map_to_dict(dataForm)

                        let username_in = data?.username || null
                        let password = data?.password || null
                        let keep_alive = data?.keep_alive || false

                        let response = await fetch(location.origin + "/v1/users/get", {

                            method: "POST",
                            body: JSON.stringify({
                                "username": username_in,
                                "password": Array.from(btoa(password)).reverse().join("")
                            }),
                            headers: { "Content-Type": "application/json" }
                        })

                        data = await response.json()

                        if (data.status_code !== 200) {

                            alert("User tidak ditemukan atau password salah!")
                            throw new Error("User tidak ditemukan atau password salah!")
                        }

                        let contents = data?.contents || []
                        let content = contents.length > 0 ? contents[0] : null

                        user_id = content?.id || null
                        username = content?.username || null

                        if (keep_alive) {

                            localStorage.setItem("id", user_id)
                            localStorage.setItem("user", username)
                            localStorage.setItem("keepAlive", keep_alive)
                            localStorage.setItem("token", null)
                        }

                        userLoginForm.parentElement.classList.add("none")

                        let w = userLoginForm.parentElement
                        let g = w?.parentElement
                        g.style.display = "none"
                    }
                })

                if (transactionForm) transactionForm.addEventListener("submit", async (ev) => {

                    let target = ev && ev?.target

                    if (target) {

                        ev.preventDefault()

                        if (user_id > 0) {

                            let dataForm = new FormData(target)
                            let data = map_to_dict(dataForm)

                            let dataIncluded = {}
                            dataIncluded.payment_type = data?.payment_type
                            dataIncluded.payment_paid = false
                            dataIncluded.user_id = user_id
                            dataIncluded.username = username
                            dataIncluded.product_id = product_id

                            let check = product_id && user_id && username

                            if (!check) {

                                alert("Ada kesalahan input!")
                                throw new Error("Something wrong!")
                            }

                            let response = await fetch(location.origin + "/v1/transactions/registry", {

                                method: "POST",
                                body: JSON.stringify(dataIncluded),
                                headers: { "Content-Type": "application/json" }
                            })

                            data = await response.json()

                            if (data.status_code !== 200) {

                                alert(data.message)
                                throw new Error(data.message)
                            } else {

                                alert("Selamat, transaksi berhasil! silahkan menunggu pesanan anda dikirim")
                                throw new Error("Only Send in Database for exercise!")
                            }

                        } else {

                            global.alert("Belum ter Registrasi sebagai member! Silahkan mengisi formulir User Registration / Login")
                        }
                    }
                })
            }
        }

        let removeCache = document.querySelector("input[type='submit']#removeCache")
        if (removeCache) {

            removeCache.addEventListener("click", (e) => {

                let target = e && e.target

                if (target) {

                    e.preventDefault()
                    e.stopPropagation()

                    localStorage.clear()
                    document.cookie = ""

                    alert("menghapus sampah, berhasil!")
                }
            })
        }
    }

    function setup(e) {

        if (document.readyState == "complete") {

            if (typeof main == "function") main(new CustomEvent("Ready", e))
            main = null;
        }
    }

    global.addEventListener("load", setup, false)
    document.addEventListener("readystatechange", setup, false)
    global.addEventListener("DOMContentLoader", setup, false)
    setup({})

})(window)
