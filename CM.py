import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def plot(name, input, title, fractions, del_fractions, uv_color, conductivity_color, buffer_color, marker_color,mark_maxima, maxima_type,
        maxima_threshhold, salt, buffer, akta_type, output_datatype):
    data = pd.DataFrame({
    'Volume_ml': input.iloc[:, 0],
    'mAU': input.iloc[:, 1],
    'Volume_grad': input.iloc[:, 4],
    'Gradient_percentB': input.iloc[:, 5],
    'Fraction_vol': input.iloc[:, 10],
    'Fraction': input.iloc[:, 11],
    'Cond': input.iloc[:, 3]
    })

    # Create figure
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Plot uv
    uv_line, = ax1.plot(data['Volume_ml'], data['mAU'], color=uv_color, lw=2, label='UV Absorption (mAU)')
    
    if mark_maxima == True:
        # Add red dot at maximum
        # Find maxima
        peaks= find_peaks(data.iloc[:, 1], prominence=maxima_threshhold, plateau_size=[0,10], width =[0,750])
        for peaks in peaks[0]:
            max_x = data['Volume_ml'][peaks]
            max_y = data['mAU'][peaks]
            plt.plot(max_x, max_y, 'o',color=marker_color, markersize=6)
            if maxima_type == 'mL':
                # Annotate with coordinates
                plt.annotate(f'{max_x:.1f} mL', 
                        xy=(max_x, max_y), 
                        xytext=(10, 10),  # offset in points
                        fontsize=8,
                        color= marker_color,
                        textcoords='offset points',
                    ha='center')
            elif maxima_type == 'mAU':
                # Annotate with coordinates
                plt.annotate(f'{max_y:.1f} mAU', 
                    xy=(max_x, max_y), 
                xytext=(10, 10),  # offset in points
                fontsize=8,
                color= marker_color,
                textcoords='offset points',
                ha='center')
    
    # Set labels for each axis
    ax1.set_xlabel('Elution Volume (mL)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('UV Absorption (mAU)', fontsize=12, fontweight='bold', color=uv_color)

    # Style the tick parameters for each axis to match their respective colors
    ax1.tick_params(axis='y', labelcolor=uv_color)

    # Set appropriate ranges for each axis
    x_lim = data["Volume_ml"].max()
    y_lim = data["mAU"].max() + data["mAU"].max()*0.2
    y_limmin = data["mAU"].min()
    ax1.set_xlim(0, x_lim)
    ax1.set_ylim(y_limmin, y_lim)

    # Transparent grey boxes for marking fraction
    for frac in fractions:
        frac_number = str(frac)
        next_number = str(frac+1)
        if akta_type == "small":
            vol_lower = data[data['Fraction'] == f"T{frac_number}"]['Fraction_vol']
            vol_higher = data[data['Fraction'] == f"T{next_number}"]['Fraction_vol']
        elif akta_type == "large":
            vol_lower = data[data['Fraction'] == frac_number]['Fraction_vol']
            vol_higher = data[data['Fraction'] == next_number]['Fraction_vol']
        middle = (vol_lower.iloc[0] + vol_higher.iloc[0])/2
        ax1.axvspan(vol_lower.iloc[0], vol_higher.iloc[0], color='gray', alpha=0.3)
        ax1.text(middle, ax1.get_ylim()[1]*0.7, f'F{frac}', ha='center', va='center', fontsize=6, color='black')

    y_pos = y_limmin + (y_lim-y_limmin)*0.04
   # mark the fractions
    for vol, frac in zip(data['Fraction_vol'], data['Fraction']):
        if pd.notna(vol) and pd.notna(frac) and frac not in del_fractions:  # Skip NaN values
            ax1.axvline(x=vol, color='gray', linestyle=':', alpha=0.5, ymin=0, ymax=0.04)
            ax1.text(vol,y_pos, str(frac).strip('""'),
                    rotation=90, va='bottom', ha='center', fontsize=8)


    # Title with experimental details
    ax1.set_title(title, fontsize=16, fontweight='bold', pad=20)

    if buffer == True and salt == False:
        ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis
        buffer_line, = ax2.plot(data['Volume_grad'],data['Gradient_percentB'], color=buffer_color, lw=2,
                        linestyle='--', label='Buffer B (%)') #plot buffer line
        ax2.set_ylabel('Buffer B (%)', fontsize=12, fontweight='bold', color=buffer_color) #label y axis
        ax2.tick_params(axis='y', labelcolor=buffer_color)
        ax2.set_ylim(0, 105)  # Slightly above 100% for better visibility

    elif salt == True and buffer == False:
        ax2 = ax1.twinx()  # Create a third y-axis
        conductivity_line, = ax2.plot(data['Volume_ml'], data['Cond'], color=conductivity_color, lw=2,
                                label='Conductivity (mS/cm)')
        ax2.set_ylabel('Conductivity (mS/cm)', fontsize=12, fontweight='bold', color=conductivity_color)
        ax2.tick_params(axis='y', labelcolor=conductivity_color)
        y_lim_salt = data['Cond'].max() + data['Cond'].max()*0.2
        ax2.set_ylim(0, y_lim_salt)

    elif salt == True and buffer == True:
        ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis
        buffer_line, = ax2.plot(data['Volume_grad'],data['Gradient_percentB'], color=buffer_color, lw=2,
                        linestyle='--', label='Buffer B (%)') #plot buffer line
        ax2.set_ylabel('Buffer B (%)', fontsize=12, fontweight='bold', color=buffer_color) #label y axis
        ax2.tick_params(axis='y', labelcolor=buffer_color)
        ax2.set_ylim(0, 105)  # Slightly above 100% for better visibility
    
        ax3 = ax1.twinx()  # Create a third y-axis
        # Offset the third y-axis to the right
        ax3.spines['right'].set_position(('outward', 60))
        conductivity_line, = ax3.plot(data['Volume_ml'], data['Cond'], color=conductivity_color, lw=2,
                                label='Conductivity (mS/cm)')
        ax3.set_ylabel('Conductivity (mS/cm)', fontsize=12, fontweight='bold', color=conductivity_color)
        ax3.tick_params(axis='y', labelcolor=conductivity_color)
        y_lim_salt = data['Cond'].max() + data['Cond'].max()*0.2
        ax3.set_ylim(0, y_lim_salt)

    

    if salt == True and buffer == True:
        # Create combined legend
        lines = [uv_line, conductivity_line, buffer_line]
    elif salt == False and buffer == True:
        # Create combined legend
        lines = [uv_line, buffer_line]
    elif salt == True and buffer == False:
         lines = [uv_line, conductivity_line]
    elif salt == False and buffer == False:
        lines = [uv_line]

    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, framealpha=0.9, fontsize=11)

    # Adjust layout
    plt.tight_layout()
    plt.savefig(f'{name}.{output_datatype}')