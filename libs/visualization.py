import os
import sys
import plotly.express as px

def generate_market_map(df):
    """Generate Treemap visualization."""
    if df.empty:
        print("No data to visualize.")
        return

    print("Generating Market Map...")
    
    # Create Treemap
    fig = px.treemap(
        df,
        path=[px.Constant("Portfolio"), "Symbol"],
        values="Market Value",
        color="Change %",
        color_continuous_scale=["red", "#404040", "green"],
        color_continuous_midpoint=0,
        # Remove Label from hover_data to avoid HTML in tooltip. 
        # We use customdata for the texttemplate.
        hover_data={"Label": False, "Quantity": True, "Price": True, "Market Value": True, "Change %": True, "Day Change": True},
        custom_data=["Label", "Change %", "Day Change"], # Explicitly pass custom_data for texttemplate
        title="Firstrade Portfolio Market Map"
    )

    # Customize text to use the pre-formatted Label
    # We access customdata via index. 
    # custom_data[0] is Label
    fig.update_traces(
        texttemplate="%{customdata[0]}",
        textposition="middle center",
        textfont=dict(size=50, family="Arial"), # Changed to Arial as requested
        hovertemplate="<b>%{label}</b><br>Market Value: $%{value:,.2f}<br>Change: %{customdata[1]:.2f}%<br>Day Change: %{customdata[2]:+.2f}<extra></extra>"
    )
    
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25),
        # Remove uniformtext to allow large fonts
        # uniformtext=dict(minsize=10, mode='hide')
    )
    
    output_file = "market_map.html"
    fig.write_html(output_file)
    print(f"Market Map saved to {output_file}")

    # Export to image
    image_file = "market_map.png"
    try:
        fig.write_image(image_file, width=1920, height=1080)
        print(f"Market Map image saved to {image_file}")
    except Exception as e:
        print(f"Failed to save image: {e}")
        print("Ensure 'kaleido' is installed: pip install kaleido")
    
    # Try to open the file
    try:
        if sys.platform == 'linux':
            os.system(f"xdg-open {output_file}")
        elif sys.platform == 'darwin':
            os.system(f"open {output_file}")
        elif sys.platform == 'win32':
            os.startfile(output_file)
    except Exception:
        pass
