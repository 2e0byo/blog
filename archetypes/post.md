---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
categories: ["{{ replace (replace .Dir "post/" "") "/" "" | title }}"]
---
