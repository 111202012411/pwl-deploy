(async global => {

    let { last_modified_to_str, noctx, map_to_dict } = await import("/utils.js")

    async function template_product(data) {

        let parent = document.createElement("div")
        let layer1 = document.createElement("div")
        let layer2 = document.createElement("div")

        let title = document.createElement("div")
        let titleSpan = document.createElement("span")
        let image = document.createElement("img")
        let modified = document.createElement("div")
        let modifiedSpan = document.createElement("span")
        let description = document.createElement("div")
        let descriptionSpan = document.createElement("span")
        let removeEl = document.createElement("div")
        let removeSpan = document.createElement("div")
        let buy = document.createElement("div")
        let buySpan = document.createElement("span")
        let price = document.createElement("div")
        let priceSpan = document.createElement("span")

        parent.classList.add("item", "product-item", "product-id-" + data.id)
        layer1.classList.add("item", "product-item")
        layer2.classList.add("item", "product-item")

        title.classList.add("item", "product-title")
        modified.classList.add("item", "product-modified")
        description.classList.add("item", "product-description")
        removeEl.classList.add("item", "product-remove", "none")
        buy.classList.add("item", "product-buy")
        price.classList.add("item", "product-price")

        let url = data?.photo || "/icon.png"
        let formatter = new Intl.NumberFormat("ru-RU", {
            style: "currency",
            currency: "RUB"
        })

        image.setAttribute("src", url)
        image.setAttribute("width", "192px")
        image.setAttribute("height", "192px")

        titleSpan.textContent = data.name
        modifiedSpan.textContent = last_modified_to_str(data.modified)
        descriptionSpan.textContent = data.description
        removeSpan.textContent = "X"
        buySpan.textContent = "Buy"
        priceSpan.textContent = formatter.format(data.price)

        title.appendChild(titleSpan)
        modified.appendChild(modifiedSpan)
        description.appendChild(descriptionSpan)
        removeEl.appendChild(removeSpan)
        buy.appendChild(buySpan)
        price.appendChild(priceSpan)

        parent.dataset.id = data.id
        parent.dataset.name = data.name
        parent.dataset.category = data.categories.join('|')
        removeEl.addEventListener("click", (ev) => {

            if (global.confirm("Yakin mau menghapus product ini?")) {

                // queue delete assign product selected
                
                fetch(location.origin + "/v1/products/remove", {

                    method: "DELETE",
                    body: JSON.stringify({
                        name: parent.dataset.name
                    })

                }).then((response) => {

                    response.json().then((res) => {

                        if (res.status_code === 200) location.reload()
                        else global.alert("Error: " + res.message)

                    }).catch((err) => {

                        global.alert("terjadi kesalahan pada server!")
                    })

                }).catch((err) => {

                    global.alert("gagal meminta permintaan penghapusan product!")
                })
            }
        })

        buy.addEventListener("click", (ev) => {

            let url = location.origin + "/buy.html?product_id=" + data.id

            // change pageview
            location.href = url

            // if failed change
            if (location.pathname == "/" || location.pathname == "/index.html") 
                global.open(url)
        })

        // switch
        layer1.appendChild(image)
        layer1.appendChild(title)
        
        layer1.appendChild(modified)
        layer1.appendChild(description)
        layer2.appendChild(removeEl)
        layer2.appendChild(buy)
        layer2.appendChild(price)

        parent.appendChild(layer1)
        parent.appendChild(layer2)

        return parent
    }

    async function main(e) {

        let response = await fetch(location.origin + "/v1/products/enrolls", {
            method: "POST",
            body: JSON.stringify({
                count: 20
            })
        })

        let data = await response.json()
        let galleryEl = document.querySelector("div.gallery")

        let adminButton = document.querySelector("a#admin")
        adminButton.addEventListener("click", (ev) => {

            let v = global.prompt("Insert admin password:")

            if (v == "admin") {

                let productInsert = document.querySelector("div.item.product-insert")
                productInsert.classList.remove("none")
    
                for (let removeEl of document.querySelectorAll(".item.product-remove"))
                    removeEl.classList.remove("none")
            }
        })

        /* build element */
        if ("contents" in data)
            for (let content of data.contents)
                galleryEl.appendChild(await template_product(content))

        /* insert new product */
        let insertNewProductEl = document.createElement("div")
        insertNewProductEl.classList.add("item", "product-insert", "none")
        galleryEl.appendChild(insertNewProductEl)

        let popupShadow = document.querySelector("div.shadow-popup")
        
        insertNewProductEl.addEventListener("click", (ev) => {

            if (popupShadow)
                if (popupShadow.classList.contains("none"))
                    popupShadow.classList.remove("none")

        })

        let popupExit = document.querySelector("div.shadow-popup button.exit")

        popupExit.addEventListener("click", (ev) => {

            if (popupShadow)
                if (!popupShadow.classList.contains("none"))
                    popupShadow.classList.add("none")

        })

        let productAdd = document.querySelector("form#productAdd")

        if (productAdd)
            productAdd.addEventListener("submit", (ev) => {

                let target = ev && ev.target

                if (target) {

                    ev.preventDefault()

                    if (target instanceof HTMLFormElement) {

                        let formData = new FormData(target)
                        let data = map_to_dict(formData)

                        fetch(location.origin + "/v1/products/registry", {

                            method: "POST",
                            body: JSON.stringify(data)

                        }).then((response) => {

                            response.json().then((res) => {

                                if (res.status_code == 200) location.reload()    
                                else global.alert("Error: " + res.message)

                            }).catch((err) => {

                                global.alert("terjadi kesalahan pada server!")
                            })
        
                        }).catch((err) => {
        
                            global.alert("gagal meminta permintaan penghapusan product!")
                        })
                    }
                }
            })

        let inputSearch = document.querySelector("div.search input[type=text][placeholder=Search]")
        let buttonSearch = document.querySelector("div.search button")

        /* create hidden element */
        let fragment = document.createDocumentFragment()
        let galleryStoreEl = document.createElement("div")
        fragment.appendChild(galleryStoreEl)
        /* create hidden element */

        // make memoize variable store
        let startStoreEl = true

        let searchHandler = () => {

            let context = inputSearch.value.trim()
            inputSearch.value = context

            // store
            if (startStoreEl)
                for (let child of Array.from(galleryEl.children)) galleryStoreEl.appendChild(child)
            
            // make store ended to the next step
            startStoreEl = false

            // clear
            for (let child of Array.from(galleryEl.children)) child.remove()
            
            // update
            if (context.length > 0) {

                if ("contents" in data)
                    for (let content of data.contents)
                        if (context.includes(content.name) || content.name.includes(context))
                            template_product(content).then(el => {

                                galleryEl.appendChild(el)
                            })

            } else for (let child of Array.from(galleryStoreEl.children)) galleryEl.appendChild(child.cloneNode(true))

            // upadte event listener
            for (let child of Array.from(galleryEl.children))
                child.addEventListener("click", (ev) => {

                    if (child.dataset?.id) {

                        let url = location.origin + "/buy.html?product_id=" + child.dataset.id

                        // change pageview
                        location.href = url
            
                        // if failed change
                        if (location.pathname == "/" || location.pathname == "/index.html") 
                            global.open(url)
                    } else {

                        global.alert("Error: product_id not found!")
                    }
                })
        }

        // inputSearch.addEventListener("keyup", searchHandler)
        buttonSearch.addEventListener("click", searchHandler)
        document.body.addEventListener("contextmenu", noctx)
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
