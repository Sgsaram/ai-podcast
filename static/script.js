const button_get = document.getElementById("button-get");
const button_clear = document.getElementById("button-clear");
const output = document.getElementById("output");
const loading = document.getElementById("loading");
const description = document.getElementById("description");
const link = document.getElementById("link");
const required = document.getElementById("required");
const views = document.getElementById("views");
const recommendations = document.getElementById("recommendations");
const new_tag = document.getElementById("new-tag");
const tags = document.getElementById("tags");

const api_url = "http://127.0.0.1:8000/process"

let bad_desc = false;
let tags_list = [];

function get_html_tags() {
    res = "";
    for (let tag of tags_list) {
        res += '<span class="rounded-2xl bg-violet-500 p-1 px-5 mx-1 my-1"><span class="text-white font-semibold text-sm">' + tag + '</span></span>';
    }
    return res;
}

function update_tags() {
    tags.innerHTML = get_html_tags();
}

function remove_tag(value) {
    const index = tags_list.indexOf(value);
    if (index != -1) {
        tags_list.splice(index, 1);
    }
}

function add_tag(value) {
    tags_list.push(value);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function handle_button_get() {
    const input_text = description.value;
    if (input_text.trim().length == 0) {
        description.classList.add("border-rose-500");
        description.classList.remove("border-blue-400");
        required.classList.remove("hidden");
        bad_desc = true;
        return;
    }
    const link_text = link.value;

    output.classList.add("hidden");
    loading.classList.add("flex");
    loading.classList.remove("hidden");
    button_get.classList.add("hidden");

    const post_data = {
        description: input_text,
        link: link_text,
    };

    views.textContent = -179;
    let text_to_print = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut sagittis sapien elit, sed elementum nisl rhoncus congue. Quisque a vestibulum justo, ac sollicitudin mi. In viverra aliquam ex viverra ullamcorper. Suspendisse mauris ligula, malesuada in arcu vitae, ultrices pharetra purus. Duis posuere dolor eu ante rutrum tincidunt. Integer cursus, ex.";
    recommendations.textContent = "";

    try {
        const response = await fetch(api_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(post_data),
        })
        const result = await response.json();
        views.textContent = result.views;
        text_to_print = result.recommendation;
    } catch(error) {
        console.error("Error:", error);
        console.log("Reload the page");
    }

    loading.classList.add("hidden");
    loading.classList.remove("flex");
    output.classList.remove("hidden");
    for (let i = 0; i < text_to_print.length; i++) {
        recommendations.textContent += text_to_print[i];
        await sleep(1);
    }
}

button_get.addEventListener("click", handle_button_get);
button_clear.addEventListener(
    "click",
    () => {
        output.classList.add("hidden");
        button_get.classList.remove("hidden")
    }
);
description.addEventListener(
    "click",
    () => {
        if (bad_desc) {
            required.classList.add("hidden");
            description.classList.add("border-blue-400");
            description.classList.remove("border-rose-500");
            bad_desc = false;
        }
    }
)

button_get.addEventListener(
    "mousedown",
    () => {
        button_get.classList.add("bg-blue-400");
        button_get.classList.remove("bg-blue-500");
    }
);

button_get.addEventListener(
    "mouseup",
    () => {
        button_get.classList.add("bg-blue-500");
        button_get.classList.remove("bg-blue-400");
    }
);

button_get.addEventListener(
    "mouseleave",
    () => {
        button_get.classList.add("bg-blue-500");
        button_get.classList.remove("bg-blue-400");
    }
);


button_clear.addEventListener(
    "mousedown",
    () => {
        button_clear.classList.add("bg-rose-400");
        button_clear.classList.remove("bg-rose-500");
    }
);

button_clear.addEventListener(
    "mouseup",
    () => {
        button_clear.classList.add("bg-rose-500");
        button_clear.classList.remove("bg-rose-400");
    }
);

button_clear.addEventListener(
    "mouseleave",
    () => {
        button_clear.classList.add("bg-rose-500");
        button_clear.classList.remove("bg-rose-400");
    }
);


new_tag.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        if (new_tag.value.trim() != "") {
            add_tag(new_tag.value.trim());
            update_tags();
            new_tag.value = "";
        }
    }
});

