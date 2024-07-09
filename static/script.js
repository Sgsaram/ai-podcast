const button_get = document.getElementById("button-get");
const button_clear = document.getElementById("button-clear");
const output = document.getElementById("output");
const loading = document.getElementById("loading");
const description = document.getElementById("description");
const title = document.getElementById("title");
const link = document.getElementById("link");
const required_title = document.getElementById("required-title");
const required_desc = document.getElementById("required-desc");
const views = document.getElementById("views");
const recommendations = document.getElementById("recommendations");
const new_tag = document.getElementById("new-tag");
const tags = document.getElementById("tags");

const api_url = "http://127.0.0.1:8000/process"

let bad_desc = false;
let bad_title = false;
let tags_list = [];

let x_mark_svg = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>';

function get_html_tags() {
    res = "";
    for (let tag of tags_list) {
        res += '<span class="cursor-pointer rounded-2xl bg-violet-500 hover:bg-violet-400 p-1 pl-5 pr-4 mx-1 my-1 flex justify-center items-center" id="' + tag + '"><span class="text-white font-semibold text-sm">' + tag + '</span><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" class="ml-1 size-4"><path fill-rule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 0 1 3.878.512.75.75 0 1 1-.256 1.478l-.209-.035-1.005 13.07a3 3 0 0 1-2.991 2.77H8.084a3 3 0 0 1-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 0 1-.256-1.478A48.567 48.567 0 0 1 7.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 0 1 3.369 0c1.603.051 2.815 1.387 2.815 2.951Zm-6.136-1.452a51.196 51.196 0 0 1 3.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 0 0-6 0v-.113c0-.794.609-1.428 1.364-1.452Zm-.355 5.945a.75.75 0 1 0-1.5.058l.347 9a.75.75 0 1 0 1.499-.058l-.346-9Zm5.48.058a.75.75 0 1 0-1.498-.058l-.347 9a.75.75 0 0 0 1.5.058l.345-9Z" clip-rule="evenodd" /></svg></span>';
    }
    return res;
}

function remove_tag(value) {
    const index = tags_list.indexOf(value);
    if (index != -1) {
        tags_list.splice(index, 1);
    }
}

function update_tags() {
    tags.innerHTML = get_html_tags();
    for (let tag of tags_list) {
        document.getElementById(tag).addEventListener("click", function(event) {
            remove_tag(tag);
            update_tags();
        })
    }
}

function scrollToBottom() {
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
    });
}

function add_tag(value) {
    tags_list.push(value);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function handle_button_get() {
    const input_text = description.value;
    const title_text = title.value;
    let exit_flag = false;
    if (input_text.trim().length == 0) {
        description.classList.add("border-rose-500");
        description.classList.remove("border-blue-400");
        required_desc.classList.remove("hidden");
        bad_desc = true;
        exit_flag = true;
    }
    if (title_text.trim().length == 0) {
        title.classList.add("border-rose-500");
        title.classList.remove("border-blue-400");
        required_title.classList.remove("hidden");
        bad_title = true;
        exit_flag = true;
    }
    if (exit_flag) {
        return;
    }
    const link_text = link.value;
    const radio_buttons = document.querySelectorAll('input[name="options"]');
    let category_text = null;
    radio_buttons.forEach(radio => {
        if (radio.checked) {
            category_text = radio.id;
        }
    })

    output.classList.add("hidden");
    loading.classList.add("flex");
    loading.classList.remove("hidden");
    button_get.classList.add("hidden");

    const post_data = {
        title: title_text,
        description: input_text,
        tags: tags_list,
        link: link_text,
        category: category_text,
    };
    console.log(post_data);

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
        text_to_print = text_to_print.replace(/\n/g, "<br>");
    } catch(error) {
        console.error("Error:", error);
        console.log("Reload the page");
    }

    loading.classList.add("hidden");
    loading.classList.remove("flex");
    output.classList.remove("hidden");

    // recommendations.innerHTML = text_to_print;
    for (let i = 0; i < text_to_print.length; i++) {
        recommendations.innerHTML = text_to_print.slice(0, i);
        scrollToBottom();
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
            required_desc.classList.add("hidden");
            description.classList.add("border-blue-400");
            description.classList.remove("border-rose-500");
            bad_desc = false;
        }
    }
)
title.addEventListener(
    "click",
    () => {
        if (bad_title) {
            required_title.classList.add("hidden");
            title.classList.add("border-blue-400");
            title.classList.remove("border-rose-500");
            bad_title = false;
        }
    }
)

new_tag.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        let new_name = new_tag.value.trim();
        if (new_name != "") {
            if (!tags_list.includes(new_name)) {
                add_tag(new_name);
                update_tags();
            }
            new_tag.value = "";
        }
    }
});

