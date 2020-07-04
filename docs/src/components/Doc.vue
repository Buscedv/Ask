<template>
    <main>
        <div id="content">
            <div v-for="(elem, index) in doc" :key="index" v-html="elem.outerHTML"></div>
        </div>
        <div class="meta" id="raw"></div>
        <div class="meta" id="sidebar-links"></div>
    </main>
</template>

<script>
    import config from '../../public/config.json';

    export default {
        name: 'Doc',
        data() {
            return {
                config: {},
                doc: [],
                sidebarLinks: [],
            }
        },
        async mounted() {
            this.loadConfig();
            this.fetchData();
        },
        methods: {
            loadConfig() {
                this.config = config;
            },
            fetchData: function () {
                let comp = this;
                let xhr = new XMLHttpRequest();
                const url = this.config.readmeLink;
                xhr.open("GET", url, true);
                xhr.onreadystatechange = function () {
                    if (this.readyState === XMLHttpRequest.DONE) {
                        if (this.status === 200) {
                            comp.getContent(this.responseText);
                        } else {
                            comp.markdown = '# 404 - Not Found';
                        }
                    }
                };
                xhr.send();
            },
            getContent(markdown) {
                const showdown  = require('showdown'),
                    converter = new showdown.Converter();
                const html =  converter.makeHtml(markdown);

                const raw = document.querySelector('#raw');

                raw.innerHTML = html;

                let tmpText = '';

                for (let node_i = 0; node_i < raw.childNodes.length; node_i++) {
                    const node = raw.childNodes[node_i];
                    if (node.nodeName !== '#text') {
                        if (node.textContent.substr(0, 4) === '/i/ ') {
                            let tmp = document.createElement('DIV');

                            tmp.classList.add('callout');
                            tmp.innerHTML = '<em class="callout-icon fas fa-info"></em>' +
                                '<p>' +
                                node.textContent.substr(4, node.textContent.length - 4) +
                                '</p>';

                            this.doc.push(tmp);

                        } else if (node.nodeName === 'H1' || node.nodeName === 'H2') {
                            this.sidebarLinks.push({
                                title: node.textContent,
                                link: '#' + node.id,
                                type: node.nodeName,
                                text: node.textContent,
                            });

                            if (this.sidebarLinks.length >= 2) {
                                this.sidebarLinks[this.sidebarLinks.length - 2].text += tmpText;
                                tmpText = '';
                            }

                            this.doc.push(node);
                        } else {
                            this.doc.push(node);
                            tmpText += node.textContent;
                        }
                    }
                }

                this.$emit('sidebarLinks', this.sidebarLinks)
            },
        },
    }
</script>

<style scoped>
    main {
        width: 100%;
        padding: 70px;
        height: 100%;
        padding-bottom: 0;
    }

    @media screen and (max-width: 500px) {
        main {
            padding: 30px;
        }
    }
</style>

<style>
    /* CONTENT */
    #content {
        margin-top: 30px;
        padding-top: 10px;
        margin-bottom: 120px;
        max-width: 95%;
        background-color: var(--white) !important;
    }

    #content h1, #content h2 {
        border-bottom: 2px solid var(--white);
    }

    #content h1 {
        margin-top: 40px;
        font-size: 2.5em;
        border-bottom: 2px solid var(--light);
    }

    #content h1, #content h2, #content h3, #content h4, #content h5, #content h6, #content p{
        color: var(--dark);
    }

    #content h2 {
        font-size: 2em;
    }

    #content h3 {
        font-size: 1.4em;
    }

    #content h4 {
        font-size: 1.2em;
        color: var(--medium-two);
        font-weight: normal;
        padding-top: 0;
    }

    #content h5 {
        font-size: 1em;
    }

    #content h6 {
        font-size: 0.4em;
    }

    #content p, #content li {
        color: var(--medium);
        font-size: 17px;
        line-height: 1.7;
        font-weight: 400;
    }

    #content .callout {
        padding: 0;
        background-color: var(--light);
        border-left: 4px solid var(--accent);
        font-size: 22px;
        display: flex;
        border-radius: 5px;
        margin-top: 12px;
        margin-bottom: 12px;
        width: 100%;
    }

    #content .callout .callout-icon {
        padding: 5px;
        height: 20px;
        width: 20px;
        color: var(--accent);
        border: 2px solid var(--accent);
        border-radius: 50%;
        text-align: center;
        float: left;
        margin-top: auto;
        margin-bottom: auto;
        margin-left: 10px;
    }

    #content .callout p {
        float: left;
        margin-left: 12px;
        color: var(--medium-two);
    }

    #content pre {
        padding: 10px;
        font-size: 16px;
        background-color: var(--code-bg);
        color: var(--dark);
        border-radius: 5px;
        display: flex;
        align-items: center;
        width: fit-content;
    }

    #content pre code {
        font-weight: 200;
        width: fit-content;
        height: 100%;
    }

    #content p code {
        background-color: var(--light);
        padding: 5px;
    }

    #content ul, #content ol {
        padding-inline-start: 0;
    }

    #content ol {
        counter-reset: li;
    }

    #content ol li {
        counter-increment: li;
    }

    #content ul li:not(.task-list-item)::before, #content ol li::before {
        color: var(--accent);
    }

    #content ul li::before, #content ol li::before {
        display: inline-block;
        width: auto;
        font-size: 1em;
        margin-right: 8px;
    }

    #content ol li::before {
        content: counter(li) ".";
        margin-right: 8px;
    }

    #content ul li:not(.task-list-item)::before {
        content: "\2022";
    }

    #content ul li, #content ol li {
        line-height: 1.5;
        font-size: 1em;
        list-style-type: none;
    }

    #content ul li *, #content ol li * {
        display: inline;
    }

    #content a {
        text-decoration: none;
        color: var(--accent);
    }

    #content a:hover {
        text-decoration: underline;
        text-underline-color: var(--accent);
    }

    #content blockquote {
        margin-top: 40px;
        margin-bottom: 40px;
        margin-inline-start: 0;
    }

    #content blockquote::before {
        color: var(--medium-two);
        content: open-quote;
        font-size: 4em;
        line-height: 0.1em;
        vertical-align: -0.2em;
    }

    #content blockquote p {
        color: var(--medium-two);
        font-family: sans-serif;
        font-size: 1.2em;
        display: inline;
    }

    #content table {
        width: 100%;
        border-collapse: collapse; border-spacing: 0;
    }

    #content td, th {
        border: 1px solid var(--light-dark);
        border-radius: 5px;
        height: 35px;
    }

    #content th {
        font-weight: bold;
        padding: 10px;
    }

    #content td {
        text-align: center;
        padding: 10px;
        background-color: var(--light);
    }

    .meta {
        display: none;
    }

    .activeScrollTo {
        border-color: var(--accent) !important;
    }

    @media screen and (max-width: 500px) {
        #content {
            padding-top: 30px;
        }
    }
</style>
