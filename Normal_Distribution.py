#Normal Distribution

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from io import BytesIO
import streamlit as st


# Choose the layout option
st.set_page_config(layout="wide")  # or "centered"

# Define explanations based on the value of n_rolls
def explanation_for_rolls(n_rolls):
    if n_rolls == 10:
        return """
        At 10 rolls (n=10), the results are highly variable.

        Each face may not appear equally, and some faces might not even show up.
        
        This is due to the small sample size, which makes the results seem more random and uneven.
        """
    elif n_rolls == 100:
        return """
        With 100 rolls (n=100), patterns start to emerge. 
        
        While some faces still might appear more often than others, the results are starting to balance out. 
        
        The distribution is beginning to look more predictable, but there's still noticeable variation.
        """
    elif n_rolls == 1000:
        return """
        At 1,000 rolls (n=1000), the dice's randomness becomes more balanced. 
        
        The frequencies of each face start to approach the expected probability of 1/6, and the distribution smoothens. 
        
        A bell curve is forming ^^.
        """
    elif n_rolls == 100000:
        return """
        When you roll the dice 100,000 times (n=100000), the results stabilize even more. 
        
        The frequencies are very close to the expected values, and the bell curve is clearly visible. 
        
        The randomness is minimized :).
        """
    elif n_rolls == 1000000:
        return """
        With 1,000,000 rolls (n=1000000), the results almost perfectly match the expected probabilities. 
        
        Each face appears around 16.67% of the time, and the distribution closely follows the theoretical normal distribution. :D
        """
    return ""

# Create a select box for specific values of n_rolls with small size
st.markdown("""
    <style>
        .stSelectbox > div > div {
            width: 100%;  /* Use full width to match markdown */
            max-width: 200px;  /* Set a maximum width */
            font-size: 14px;  /* Adjust the font size */
        }
    </style>
""", unsafe_allow_html=True)

# Dashboard Title & Subtitle
st.title("How does the normal distribution work in dice rolling?")
st.markdown("""
    <div style="font-size: 20px;">
        Individual dice rolls follow a uniform distribution, as each face of a fair die has an equal probability of appearing. However, as you roll the dice many times (the higher the n), the overall results from many rolls can converge to a normal distribution.
    </div>
""", unsafe_allow_html=True)

# Create two columns: one for the chart (larger) and one for the text (smaller)
col1, col2 = st.columns([1, 1])  # 50-50

# Create a multiselect for specific values of n_rolls
n_rolls = st.selectbox('Select the number of dice rolls', options=[10, 100, 1000, 100000, 1000000])


# Simulate rolling a dice n times
rolls = np.random.randint(1, 7, size=n_rolls)

# Count the frequency of each face
face_counts = np.bincount(rolls)[1:]

# Function to create dice face images with black dots
def create_dice_face(face_value):
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')  # Hide the axis to remove any background
    
    # Define the positions of the dots for each face value
    dot_positions = {
        1: [(0.5, 0.5)],
        2: [(0.25, 0.75), (0.75, 0.25)],
        3: [(0.25, 0.75), (0.5, 0.5), (0.75, 0.25)],
        4: [(0.25, 0.75), (0.75, 0.75), (0.25, 0.25), (0.75, 0.25)],
        5: [(0.25, 0.75), (0.75, 0.75), (0.5, 0.5), (0.25, 0.25), (0.75, 0.25)],
        6: [(0.25, 0.75), (0.75, 0.75), (0.25, 0.5), (0.75, 0.5), (0.25, 0.25), (0.75, 0.25)]
    }
    
    # Draw the dots on the dice face with black color
    for pos in dot_positions[face_value]:
        dot = RegularPolygon(pos, numVertices=30, radius=0.08, orientation=np.pi/4, color='black')
        ax.add_patch(dot)
    
    # Save the figure to a buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent = True)
    plt.close(fig)
    buf.seek(0)
    
    return OffsetImage(plt.imread(buf), zoom=0.3)  # Reduce the zoom to make icons smaller

# Create a bar plot
fig, ax = plt.subplots()
sns.barplot(x=np.arange(1, 7), y=face_counts, color = '#99B7CF',  ax=ax)

# Remove the frame (spines) from the chart
for spine in ax.spines.values():
    spine.set_visible(False)

# Add dice face images to the x-axis labels
for i in range(6):
    imagebox = AnnotationBbox(create_dice_face(i + 1), (i, -0.02), frameon=False, box_alignment=(0.5, 1), pad=0.1)
    ax.add_artist(imagebox)

# Remove existing x-axis tick labels
ax.set_xticklabels([''] * 6)

# Remove x-axis tick marks (sticks)
ax.tick_params(axis='x', which='both', length=0)


# Adjust y-axis tick frequency (reduce y-axis labels by half)
y_ticks = ax.get_yticks()
ax.set_yticks(y_ticks[::2])  # Set only half the current y-ticks

# Adjust axis limits to make space for the images
ax.set_ylim(bottom=-0.1)

# Set the chart title with reduced text size and position in the top left
# ax.set_title(f'Rolling the dice {n_rolls} times', fontsize=12, loc='left')


# plt.xlabel('')
plt.ylabel('Frequency', fontsize = 7)
# plt.title('Frequency of Dice Rolls (n=1000)')
# plt.show()


with col1:
    st.markdown(f"""
    <div style="font-size: 20px; margin-top: 50px;">
        Rolling the dice {n_rolls} times:
    </div>
    """, unsafe_allow_html=True)
    # Display your plot in the first column (larger column)
    st.pyplot(plt)



with col2:
    # Display a custom markdown explanation based on the selected n_rolls
    st.markdown(f"""
    <div style="font-size:12px; color: darkgray; margin-top: 250px; max-width: 100%; padding: 10px; min-height: 150px;">
        {explanation_for_rolls(n_rolls)}
    </div>
    """, unsafe_allow_html=True)
