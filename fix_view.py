file_path = r'C:\Users\dsanc\OneDrive\Escritorio\Ingenieria En Sistemas\ALGEBRA LINEAL\Calculadora_AlgebraLineal\UI\views\main_shell.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the matrix_identities section
old_code = '''        elif method.view_type == "matrix_identities":
            view = self._ensure_matrix_identities_view()
            if self._center_container:
                self._center_container.content = view.view
                self._safe_update(self._center_container)
            if self._config_container:
                self._config_container.content = view.config_view
                self._config_container.visible = True
                self._config_visible = True
                self._safe_update(self._config_container)'''

new_code = '''        elif method.view_type == "matrix_identities":
            view = self._ensure_matrix_identities_view()
            if self._center_container:
                self._center_container.content = view.view
                self._safe_update(self._center_container)
            if self._config_container:
                self._config_container.content = view.config_view
                self._config_container.visible = True
                self._config_visible = True
                self._safe_update(self._config_container)
            # Force full page update to ensure view switch is reflected
            self.page.update()'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed matrix_identities view update!")
else:
    print("Could not find the exact code block. Let me search for it...")
    idx = content.find('elif method.view_type == "matrix_identities"')
    if idx > 0:
        print(f"Found at index {idx}")
        print(repr(content[idx:idx+500]))
    else:
        print("Not found at all!")
