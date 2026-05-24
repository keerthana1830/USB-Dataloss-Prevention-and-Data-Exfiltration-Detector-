try:
    import fpdf
    print("Found 'fpdf' module. FPDF version:", fpdf.__version__ if hasattr(fpdf, '__version__') else 'unknown')
except ImportError:
    print("Could not find 'fpdf' module.")

try:
    import fpdf2
    print("Found 'fpdf2' module. FPDF2 version:", fpdf2.__version__ if hasattr(fpdf2, '__version__') else 'unknown')
except ImportError:
    print("Could not find 'fpdf2' module.")
