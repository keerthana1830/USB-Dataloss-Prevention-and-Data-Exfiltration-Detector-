try:
    from fpdf import FPDF
    import io
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Test PDF', 0, 1, 'C')
    output = pdf.output()
    
    if isinstance(output, bytes):
        print("SUCCESS: PDF output is bytes.")
        print(f"Length: {len(output)}")
    else:
        print(f"FAILURE: PDF output is {type(output)}")
except Exception as e:
    print(f"ERROR: {e}")
