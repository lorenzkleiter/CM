import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def plot(name, input_data, akta_type, **kwargs):
    """
    Plot chromatography data with flexible configuration options.
    
    Parameters:
    -----------
    name : str
        Output filename (without extension)
    input_data : pandas.DataFrame
        Input chromatography data
    akta_type : str, necessary due to difference in file format
        AKTA system type ('small' or 'large')

    Keyword Arguments:
    ------------------
    title : str, default=''
        Plot title
    fractions : list, default=[]
        List of fraction numbers to highlight
    fraction_text: integer, default = 0.7
        height of fraction test marking fractions
    del_fraction_markings : list, default=[]
        Fractions to exclude from marking     
    uv_color : str, default='#1f77b4'
        Color for UV absorption line
    conductivity_color : str, default='#d68924'
        Color for conductivity line
    buffer_color : str, default='#2ca02c'
        Color for buffer gradient line
    marker_color : str, default='#dc143c'
        Color for peak markers
    mark_maxima : bool, default=False
        Whether to mark peak maxima
    maxima_type : str, default='mL'
        Type of maxima annotation ('mL' or 'mAU')
    maxima_threshold : float, default=50
        Prominence threshold for peak detection
    max_width : int, default=10000
        Maximum width for peak detection
    salt : bool, default=False
        Whether to show conductivity data
    buffer : bool, default=False
        Whether to show buffer gradient
    output_datatype : str, default='svg'
        Output file format
    figsize : tuple, default=(12, 7)
        Figure size (width, height)
    x_lim: int. default= max X value
        limit of the x axis    
    """
    
    # Set default values
    defaults = {
        'title': '',
        'fractions': [],
        'fraction_text': 0.7,
        'del_fraction_markings': [],
        'uv_color': '#1f77b4',
        'conductivity_color': '#d68924',
        'buffer_color': '#2ca02c',
        'marker_color': '#dc143c',
        'mark_maxima': False,
        'maxima_type': 'mL',
        'maxima_threshold': 50,
        'max_width': 10000,
        'salt': False,
        'buffer': False,
        'output_datatype': 'svg',
        'figsize': (12, 7),
        'x_lim': data["Volume_ml"].max()
    }
    for key in kwargs.keys():
       if key not in ['title', 'fractions', 'del_fraction_markings', 'uv_color','conductivity_color', 'buffer_color', 'marker_color','mark_maxima','maxima_threshold', 'maxima_type', 'max_width','salt','buffer','output_datatype','figsize', 'fraction_text']:
           print(f'Warning: you might have misspelled the variable: {key}. Which means the default parameter was used')   
    # Update defaults with provided kwargs
    config = {**defaults, **kwargs}
    
    # Prepare data
    data = pd.DataFrame({
        'Volume_ml': input_data.iloc[:, 0],
        'mAU': input_data.iloc[:, 1],
        'Volume_grad': input_data.iloc[:, 4],
        'Gradient_percentB': input_data.iloc[:, 5],
        'Fraction_vol': input_data.iloc[:, 10],
        'Fraction': input_data.iloc[:, 11],
        'Cond': input_data.iloc[:, 3]
    })

    # Create figure
    fig, ax1 = plt.subplots(figsize=config['figsize'])

    # Plot UV absorption
    uv_line, = ax1.plot(data['Volume_ml'], data['mAU'], 
                        color=config['uv_color'], lw=2, 
                        label='UV Absorption (mAU)')
    
    
    # Set labels and styling for primary axis
    ax1.set_xlabel('Elution Volume (mL)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('UV Absorption (mAU)', fontsize=12, fontweight='bold', 
                   color=config['uv_color'])
    ax1.tick_params(axis='y', labelcolor=config['uv_color'])

    # Set y axis limits
    y_lim = data["mAU"].max() + data["mAU"].max() * 0.2
    y_limmin = data["mAU"].iloc[100:].min()
    y_limmin = y_limmin - y_lim * 0.02
    ax1.set_xlim(0, x_lim)
    ax1.set_ylim(y_limmin, y_lim)

        # Mark maxima if requested
    if config['mark_maxima']:
        _add_maxima_markers(ax1, data, config)

    # Add fraction highlighting
    _add_fraction_highlighting(ax1, data, config, akta_type)
    
    # Add fraction markers
    _add_fraction_markers(ax1, data, config['del_fraction_markings'], akta_type, y_limmin, y_lim)

    # Set title
    ax1.set_title(config['title'], fontsize=16, fontweight='bold', pad=20)

    # Add secondary axes based on configuration
    lines = [uv_line]
    lines.extend(_add_secondary_axes(ax1, data, config))

    # Create legend
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc='upper left', frameon=True, 
               framealpha=0.9, fontsize=11)

    # Finalize and save
    plt.tight_layout()
    plt.savefig(f'{name}.{config["output_datatype"]}', format=config["output_datatype"])

"""
Helper Functions
"""
def _add_maxima_markers(ax, data, config):
    """Add markers and annotations for peak maxima."""
    peaks = find_peaks(data.iloc[:, 1], 
                      prominence=config['maxima_threshold'], 
                      plateau_size=[0, 10], 
                      width=[0, config['max_width']])
    for peak in peaks[0]:
        max_x = data['Volume_ml'][peak]
        max_y = data['mAU'][peak]
        ax.plot(max_x, max_y, 'o', color=config['marker_color'], markersize=6)
        
        # Add annotation based on type
        if config['maxima_type'] == 'mL':
            annotation_text = f'{max_x:.1f} mL'
        elif config['maxima_type'] == 'mAU':
            annotation_text = f'{max_y:.1f} mAU'
        else:
            annotation_text = f'{max_x:.1f} mL'  # fallback
        
        ax.annotate(annotation_text, 
                   xy=(max_x, max_y), 
                   xytext=(10, 10),
                   fontsize=8,
                   color=config['marker_color'],
                   textcoords='offset points',
                   ha='center')


def _add_fraction_highlighting(ax, data, config, akta_type):
    """Add transparent boxes for fraction highlighting."""
    for frac in config['fractions']:
        frac_number = str(frac)
        next_number = str(frac + 1)
        
        if akta_type == "small":
            vol_lower = data[data['Fraction'] == f"T{frac_number}"]['Fraction_vol']
            vol_higher = data[data['Fraction'] == f"T{next_number}"]['Fraction_vol']
        elif akta_type == "large":
            vol_lower = data[data['Fraction'] == frac_number]['Fraction_vol']
            vol_higher = data[data['Fraction'] == next_number]['Fraction_vol']
        
        if not vol_lower.empty and not vol_higher.empty:
            middle = (vol_lower.iloc[0] + vol_higher.iloc[0]) / 2
            ax.axvspan(vol_lower.iloc[0], vol_higher.iloc[0], 
                      color='gray', alpha=0.3)
            ax.text(middle, ax.get_ylim()[1] * config['fraction_text'], f'F{frac}', 
                   ha='center', va='center', fontsize=6, color='black')


def _add_fraction_markers(ax, data, del_fraction_markings, akta_type, y_limmin, y_lim):
    """Add vertical lines and labels for fraction markers."""
    y_pos = y_limmin + (y_lim - y_limmin) * 0.04

    del_fractions = []                              #converts desired fraction do string for filtering
    for frac in del_fraction_markings:
        string = str(frac)
        if akta_type == 'small':    del_fractions.append(f'T{string}')
        elif akta_type == 'large':    del_fractions.append(f'{string}')

    for vol, frac in zip(data['Fraction_vol'], data['Fraction']):
        if pd.notna(vol) and pd.notna(frac) and frac not in del_fractions and frac not in ['Waste', 'Frac']:
            ax.axvline(x=vol, color='gray', linestyle=':', alpha=0.5, 
                      ymin=0, ymax=0.04)
            ax.text(vol, y_pos, str(frac).strip('""'),
                   rotation=90, va='bottom', ha='center', fontsize=8)


def _add_secondary_axes(ax1, data, config):
    """Add secondary axes for buffer and/or conductivity data."""
    additional_lines = []
    
    # Determine which secondary axes to add
    show_buffer = config['buffer']
    show_salt = config['salt']
    
    if show_buffer and not show_salt:
        # Only buffer
        ax2 = ax1.twinx()
        buffer_line, = ax2.plot(data['Volume_grad'], data['Gradient_percentB'], 
                               color=config['buffer_color'], lw=2,
                               linestyle='--', label='Buffer B (%)')
        ax2.set_ylabel('Buffer B (%)', fontsize=12, fontweight='bold', 
                      color=config['buffer_color'])
        ax2.tick_params(axis='y', labelcolor=config['buffer_color'])
        ax2.set_ylim(0, 105)
        additional_lines.append(buffer_line)
        
    elif show_salt and not show_buffer:
        # Only conductivity
        ax2 = ax1.twinx()
        conductivity_line, = ax2.plot(data['Volume_ml'], data['Cond'], 
                                     color=config['conductivity_color'], lw=2,
                                     label='Conductivity (mS/cm)')
        ax2.set_ylabel('Conductivity (mS/cm)', fontsize=12, fontweight='bold', 
                      color=config['conductivity_color'])
        ax2.tick_params(axis='y', labelcolor=config['conductivity_color'])
        y_lim_salt = data['Cond'].max() + data['Cond'].max() * 0.2
        ax2.set_ylim(0, y_lim_salt)
        additional_lines.append(conductivity_line)
        
    elif show_buffer and show_salt:
        # Both buffer and conductivity
        ax2 = ax1.twinx()
        buffer_line, = ax2.plot(data['Volume_grad'], data['Gradient_percentB'], 
                               color=config['buffer_color'], lw=2,
                               linestyle='--', label='Buffer B (%)')
        ax2.set_ylabel('Buffer B (%)', fontsize=12, fontweight='bold', 
                      color=config['buffer_color'])
        ax2.tick_params(axis='y', labelcolor=config['buffer_color'])
        ax2.set_ylim(0, 105)
        additional_lines.append(buffer_line)
        
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        conductivity_line, = ax3.plot(data['Volume_ml'], data['Cond'], 
                                     color=config['conductivity_color'], lw=2,
                                     label='Conductivity (mS/cm)')
        ax3.set_ylabel('Conductivity (mS/cm)', fontsize=12, fontweight='bold', 
                      color=config['conductivity_color'])
        ax3.tick_params(axis='y', labelcolor=config['conductivity_color'])
        y_lim_salt = data['Cond'].max() + data['Cond'].max() * 0.2
        ax3.set_ylim(0, y_lim_salt)
        additional_lines.append(conductivity_line)
    
    return additional_lines

def load(name, akta_type, **kwargs):
    """
    Load chromatography data.
    
    Parameters:
    -----------
    name : str
        Input filename (without extension)
    akta_type : str, necessary due to difference in file format
        AKTA system type ('small' or 'large')

    Keyword Arguments:
    ------------------
    small_akta_filetype: str, default = 'csv'
        Type of file exported from the small akta('csv' or 'asc')
    """
    defaults = {'small_akta_filetype': 'csv'} 
    config = {**defaults, **kwargs}

    if akta_type == 'small':
        if config['small_akta_filetype'] == 'csv': data = pd.read_csv(f'{name}.csv', sep=",", encoding='utf_8', skiprows=3, header=None)
        elif config['small_akta_filetype']  == 'asc': data = pd.read_csv(f'{name}.asc', sep="\t", encoding='utf_8', skiprows=3, header=None)
        else: print("please enter 'csv' or 'asc' for small_akta_filetype")
    elif akta_type == 'large': data = pd.read_csv(f'{name}.csv', sep="\t", encoding='utf_16', skiprows=3, header=None)
    else: print("please enter 'large' or 'small' for akta_type")

    return data