(async global => {

    let { parse_numbers, parse_url_search, last_modified_to_str, noctx, map_to_dict } = await import("/utils.js")

    let userTranslationStore = []
    class UserTransaction extends Object {

        id = 0
        user_name = ""
        product_name = ""
        product_price = 0
        product_name = 0
        count = 0

        constructor(id, user_name, product_name, product_price, product_sale) {
            super()

            this.id = id
            this.user_name = user_name
            this.product_name = product_name
            this.product_price = product_price
            this.product_sale = product_sale
            this.count = 1
        }

        static init(o) {

            let find = false
            let classSelf = this

            let id = o?.id || 0
            let user_name = o?.user_name || ""
            let product_name = o?.product_name || ""
            let product_price = o?.product_price || 0
            let product_sale = o?.product_sale || 0

            if (user_name && product_name) {

                // check no dup
                for (let userTranslation of userTranslationStore) {

                    if (userTranslation.user_name == user_name &&
                        userTranslation.product_name == product_name) {

                            userTranslation.increase_amount = 1
                            find = true
                        }
                }

                if (!find) userTranslationStore.push(new classSelf(id, user_name, product_name, product_price, product_sale))
            }
        }

        static render() {

            let fragments = document.createDocumentFragment()

            for (let userTranslation of userTranslationStore) {

                fragments.appendChild(userTranslation.html)
            }

            return fragments
        }

        async remove() {

            if (this.id > 0) {

                let response = await fetch(location.origin + "/v1/transactions/remove", {

                    method: "DELETE",
                    body: JSON.stringify({
                        "id": this.id
                    }),
                    headers: {
                        "Content-Type": "application/json"
                    }
                })

                let data = await response.json()

                let status_code = data?.status_code || 400

                if (status_code == 200) {

                    location.reload()
                    return 1

                } else {

                    alert("gagal menghapus transaction!")

                }

            } else {

                alert("id transaction tidak ditemukan!")
            }
            return 0
        }

        set increase_amount(value = 0) {

            this.count += value
        }

        get html() {


            let tr = document.createElement("tr")
            let userNameTd = document.createElement("td")
            let userNameDiv = document.createElement("div")
            let produkNameTd = document.createElement("td")
            let produkBuyTd = document.createElement("td")
            let produkCountTd = document.createElement("td")
            let produkTotalTd = document.createElement("td")
            let deleteTransactionBtn = document.createElement("button")

            deleteTransactionBtn.classList.add("remove-transaction")

            userNameDiv.textContent = this.user_name
            produkNameTd.textContent = this.product_name
            produkBuyTd.textContent = this.product_price - this.product_sale
            produkCountTd.textContent = this.count
            produkTotalTd.textContent = this.count * (this.product_price - this.product_sale)

            deleteTransactionBtn.textContent = "hapus"
            userNameDiv.appendChild(deleteTransactionBtn)

            deleteTransactionBtn.addEventListener("click", ((e) => {

                let confirm = global.confirm("Apakah ingin menghapus salah satu transaksi ini?")
                
                if (confirm) this.remove()

            }).bind(this))

            userNameTd.appendChild(userNameDiv)

            tr.append(userNameTd, produkNameTd, produkBuyTd, produkCountTd, produkTotalTd)

            return tr
        }
    }

    async function main(e) {

        // load ready like defer but async + module


        // parse url search
        let params = parse_url_search(location.search)

        let maxsize = params?.maxsize || 20

        let response = await fetch(location.origin + "/v1/transactions/enrolls", {

            method: "POST",
            body: JSON.stringify({
                count: maxsize
            }),
            headers: {
                "Content-Type": "application/json"
            }
        })

        let data = await response.json()

        let contents = data?.contents || []

        let tableView = document.querySelector("table#view")
        let tableBody = tableView.querySelector("tbody")

        if (contents.length > 0) {

            for (let content of contents) {

                if (content) {

                    UserTransaction.init(content)
                }
            }

            tableBody.appendChild(UserTransaction.render())
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
