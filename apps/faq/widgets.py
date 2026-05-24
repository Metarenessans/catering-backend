import json
from django import forms
from django.utils.safestring import mark_safe

class StringListWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        # Parse value if it is a JSON string
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    value = parsed
            except json.JSONDecodeError:
                value = []
        
        if not isinstance(value, list):
            value = []
            
        values_json = json.dumps(value, ensure_ascii=False)
        
        # We will build the HTML and JavaScript
        html = f"""
        <div id="{name}-container" class="string-list-container" style="max-width: 800px;">
           <!-- Dynamic inputs will be inserted here -->
        </div>
        <button type="button" id="add-{name}-btn" class="button" style="margin-top: 8px; background: #417690; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">
            + Добавить строку
        </button>
        
        <script>
        (function() {{
            const container = document.getElementById('{name}-container');
            const addButton = document.getElementById('add-{name}-btn');
            
            function createRow(value = "") {{
                const div = document.createElement('div');
                div.className = 'string-list-item';
                div.style.display = 'flex';
                div.style.alignItems = 'center';
                div.style.marginBottom = '8px';
                div.style.gap = '8px';
                
                const input = document.createElement('input');
                input.type = 'text';
                input.name = '{name}';
                input.value = value;
                input.className = 'vTextField';
                input.style.width = '80%';
                input.style.margin = '0';
                
                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'button';
                deleteBtn.textContent = 'Удалить';
                deleteBtn.style.background = '#ba2121';
                deleteBtn.style.color = 'white';
                deleteBtn.style.border = 'none';
                deleteBtn.style.padding = '5px 10px';
                deleteBtn.style.borderRadius = '4px';
                deleteBtn.style.cursor = 'pointer';
                
                deleteBtn.addEventListener('click', function() {{
                    div.remove();
                }});
                
                div.appendChild(input);
                div.appendChild(deleteBtn);
                container.appendChild(div);
            }}
            
            // Render existing values
            const values = {values_json};
            if (values && values.length > 0) {{
                values.forEach(val => createRow(val));
            }} else {{
                createRow(); // render at least one empty input
            }}
            
            addButton.addEventListener('click', function() {{
                createRow();
            }});
        }})();
        </script>
        """
        return mark_safe(html)
        
    def value_from_datadict(self, data, files, name):
        # Fetch list of submitted values under this name
        values = data.getlist(name)
        # Clean and filter out empty strings
        cleaned = [v.strip() for v in values if v and v.strip()]
        return cleaned
