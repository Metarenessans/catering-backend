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
        <div class="string-list-widget-wrapper" style="display: block; width: 100%; max-width: 600px; box-sizing: border-box;">
            <div id="{name}-container" class="string-list-container" style="display: block; width: 100%; box-sizing: border-box;">
               <!-- Dynamic inputs will be inserted here -->
            </div>
            <div style="display: block; margin-top: 8px;">
                <button type="button" id="add-{name}-btn" class="button" style="background: #417690; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: 500;">
                    + Добавить строку
                </button>
            </div>
        </div>
        
        <script>
        (function() {{
            const container = document.getElementById('{name}-container');
            const addButton = document.getElementById('add-{name}-btn');
            
            function updateDeleteButtons() {{
                const items = container.querySelectorAll('.string-list-item');
                const deleteButtons = container.querySelectorAll('.string-list-delete-btn');
                if (items.length <= 1) {{
                    deleteButtons.forEach(btn => {{
                        btn.style.display = 'none';
                    }});
                }} else {{
                    deleteButtons.forEach(btn => {{
                        btn.style.display = 'inline-flex';
                    }});
                }}
            }}
            
            function createRow(value = "") {{
                const div = document.createElement('div');
                div.className = 'string-list-item';
                div.style.display = 'flex';
                div.style.alignItems = 'center';
                div.style.marginBottom = '8px';
                div.style.gap = '8px';
                div.style.width = '100%';
                div.style.boxSizing = 'border-box';
                
                const input = document.createElement('input');
                input.type = 'text';
                input.name = '{name}';
                input.value = value;
                input.className = 'vTextField';
                input.style.flex = '1';
                input.style.minWidth = '0';
                input.style.margin = '0';
                
                const deleteBtn = document.createElement('button');
                deleteBtn.type = 'button';
                deleteBtn.className = 'button string-list-delete-btn';
                deleteBtn.textContent = 'Удалить';
                deleteBtn.style.background = '#ba2121';
                deleteBtn.style.color = 'white';
                deleteBtn.style.border = 'none';
                deleteBtn.style.padding = '6px 12px';
                deleteBtn.style.borderRadius = '4px';
                deleteBtn.style.cursor = 'pointer';
                deleteBtn.style.height = '32px';
                deleteBtn.style.display = 'inline-flex';
                deleteBtn.style.alignItems = 'center';
                deleteBtn.style.justifyContent = 'center';
                deleteBtn.style.flexShrink = '0';
                
                deleteBtn.addEventListener('click', function() {{
                    div.remove();
                    updateDeleteButtons();
                }});
                
                div.appendChild(input);
                div.appendChild(deleteBtn);
                container.appendChild(div);
                
                updateDeleteButtons();
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
