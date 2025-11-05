import os
import matplotlib.pyplot as plt
import matplotx
import numpy as np
from typing import Dict, Any
from tools.ComparisonData import ComparisonData


class ComparisonPlotter:
    """Visualization class for ontology comparisons
    
    This class creates comparison visualizations between two ontologies,
    including overlaid spider plots, grouped lollipop plots, difference charts,
    and grouped bar charts for subcharacteristics.
    """
    
    def __init__(self):
        """Initialize with color schemes and style settings"""
        self.ontology1_color = '#3498db'  # Blue
        self.ontology2_color = '#e67e22'  # Orange
        self.improvement_color = '#27ae60'  # Green
        self.degradation_color = '#e74c3c'  # Red
        self.style = matplotx.styles.ayu["light"]
    
    def _setup_comparison_style(self) -> None:
        """Apply matplotx styling (same as existing Plotter)"""
        plt.style.use(self.style)
    
    def plot_characteristics_comparison(
        self, comparison_data: ComparisonData, output_path: str
    ) -> None:
        """Create overlaid spider plot for characteristics
        
        Creates a radar/spider plot with two overlaid plots showing the
        characteristics values for both ontologies. Uses different colors
        with filled areas for easy visual comparison.
        
        Args:
            comparison_data: ComparisonData object containing comparison data
            output_path: Base path for output directory
        """
        # Get characteristics comparison data
        characteristics_comp = comparison_data.get_characteristics_comparison()
        
        # Extract names and values for both ontologies
        names = list(characteristics_comp.keys())
        values1 = [characteristics_comp[name]['value'][comparison_data.ontology1_name] 
                   for name in names]
        values2 = [characteristics_comp[name]['value'][comparison_data.ontology2_name] 
                   for name in names]
        
        # Calculate angles and close the plots by repeating first item
        value_range = range(len(names))
        angles = [i/len(names) * 2 * np.pi for i in value_range]
        values1 += values1[:1]
        values2 += values2[:1]
        angles += angles[:1]
        
        # Create the plot
        with plt.style.context(self.style):
            ax = plt.subplot(111, polar=True)
            plt.xticks(angles[:-1], names, color='grey', size=12)
            plt.yticks([1, 2, 3, 4], ["1", "2", "3", "4"], color="grey", size='7')
            plt.ylim([0, 5])
            
            # Plot both ontologies
            ax.plot(angles, values1, linewidth=2, linestyle='solid', 
                   color=self.ontology1_color, label=comparison_data.ontology1_name)
            ax.fill(angles, values1, color=self.ontology1_color, alpha=0.3)
            
            ax.plot(angles, values2, linewidth=2, linestyle='solid', 
                   color=self.ontology2_color, label=comparison_data.ontology2_name)
            ax.fill(angles, values2, color=self.ontology2_color, alpha=0.3)
            
            plt.title('OQuaRE Characteristics Comparison')
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            
            # Save the figure
            img_dir = os.path.join(output_path, 'img')
            os.makedirs(img_dir, exist_ok=True)
            filename = f"{comparison_data.ontology1_name}_vs_{comparison_data.ontology2_name}_characteristics_comparison.png"
            plt.savefig(os.path.join(img_dir, filename), format="png", bbox_inches='tight')
            plt.clf()
    
    def plot_metrics_comparison(
        self, comparison_data: ComparisonData, output_path: str, scaled: bool = False
    ) -> None:
        """Create side-by-side lollipop plot for metrics
        
        Creates a grouped horizontal lollipop plot with two stems per metric,
        one for each ontology. Uses vertical offset to prevent overlap.
        
        Args:
            comparison_data: ComparisonData object containing comparison data
            output_path: Base path for output directory
            scaled: If True, use scaled metrics (0-5 range), otherwise use raw metrics
        """
        # Get appropriate metrics comparison
        if scaled:
            metrics_comp = comparison_data.get_scaled_metrics_comparison()
        else:
            metrics_comp = comparison_data.get_metrics_comparison()
        
        names = list(metrics_comp.keys())
        values1 = [metrics_comp[name][comparison_data.ontology1_name] for name in names]
        values2 = [metrics_comp[name][comparison_data.ontology2_name] for name in names]
        
        # Create y positions with offset for grouping
        ypos = np.arange(len(names))
        offset = 0.15
        
        with plt.style.context(self.style):
            # Plot stems for ontology 1
            plt.hlines(y=ypos - offset, xmin=0, xmax=values1, 
                      color=self.ontology1_color, linewidth=2, alpha=0.7)
            plt.plot(values1, ypos - offset, "D", color=self.ontology1_color, 
                    markersize=6, label=comparison_data.ontology1_name)
            
            # Plot stems for ontology 2
            plt.hlines(y=ypos + offset, xmin=0, xmax=values2, 
                      color=self.ontology2_color, linewidth=2, alpha=0.7)
            plt.plot(values2, ypos + offset, "D", color=self.ontology2_color, 
                    markersize=6, label=comparison_data.ontology2_name)
            
            # Add value annotations
            for i in range(len(names)):
                if scaled:
                    plt.annotate(f'{values1[i]:.2f}', 
                               xy=(values1[i] + 0.15, ypos[i] - offset - 0.05), 
                               textcoords='data', fontsize=7, 
                               color=self.ontology1_color)
                    plt.annotate(f'{values2[i]:.2f}', 
                               xy=(values2[i] + 0.15, ypos[i] + offset - 0.05), 
                               textcoords='data', fontsize=7, 
                               color=self.ontology2_color)
                else:
                    plt.annotate(f'{values1[i]:.2f}', 
                               xy=(values1[i] + max(values1 + values2) * 0.02, ypos[i] - offset - 0.05), 
                               textcoords='data', fontsize=7, 
                               color=self.ontology1_color)
                    plt.annotate(f'{values2[i]:.2f}', 
                               xy=(values2[i] + max(values1 + values2) * 0.02, ypos[i] + offset - 0.05), 
                               textcoords='data', fontsize=7, 
                               color=self.ontology2_color)
            
            plt.yticks(ypos, names)
            if scaled:
                plt.xlim([0, 5.5])
                plt.title('OQuaRE Scaled Metrics Comparison')
            else:
                plt.title('OQuaRE Metrics Comparison')
            
            plt.legend(loc='best')
            
            # Save the figure
            img_dir = os.path.join(output_path, 'img')
            os.makedirs(img_dir, exist_ok=True)
            if scaled:
                filename = f"{comparison_data.ontology1_name}_vs_{comparison_data.ontology2_name}_scaled_metrics_comparison.png"
            else:
                filename = f"{comparison_data.ontology1_name}_vs_{comparison_data.ontology2_name}_metrics_comparison.png"
            plt.savefig(os.path.join(img_dir, filename), format="png", bbox_inches='tight')
            plt.clf()
    
    def plot_metrics_difference(
        self, comparison_data: ComparisonData, output_path: str
    ) -> None:
        """Create bar chart showing metric differences
        
        Creates a horizontal bar chart showing the difference between metrics
        (ontology2 - ontology1). Positive differences (improvements) are shown
        in green, negative differences (degradations) in red. Bars are sorted
        by absolute difference magnitude.
        
        Args:
            comparison_data: ComparisonData object containing comparison data
            output_path: Base path for output directory
        """
        # Get scaled metrics comparison for differences
        metrics_comp = comparison_data.get_scaled_metrics_comparison()
        
        # Extract differences and sort by absolute magnitude
        differences = {name: data['difference'] for name, data in metrics_comp.items()}
        sorted_items = sorted(differences.items(), key=lambda x: abs(x[1]), reverse=True)
        names = [item[0] for item in sorted_items]
        diffs = [item[1] for item in sorted_items]
        
        # Assign colors based on positive/negative
        colors = [self.improvement_color if d > 0 else self.degradation_color if d < 0 else '#95a5a6' 
                 for d in diffs]
        
        ypos = np.arange(len(names))
        
        with plt.style.context(self.style):
            plt.barh(ypos, diffs, color=colors, alpha=0.7)
            plt.yticks(ypos, names)
            
            # Add zero line
            plt.axvline(x=0, color='black', linewidth=0.8, linestyle='-')
            
            # Add value annotations
            for i, diff in enumerate(diffs):
                if diff > 0:
                    plt.annotate(f'+{diff:.2f}', 
                               xy=(diff + 0.05, i), 
                               textcoords='data', fontsize=7, 
                               va='center')
                elif diff < 0:
                    plt.annotate(f'{diff:.2f}', 
                               xy=(diff - 0.05, i), 
                               textcoords='data', fontsize=7, 
                               va='center', ha='right')
                else:
                    plt.annotate('0.00', 
                               xy=(0.05, i), 
                               textcoords='data', fontsize=7, 
                               va='center')
            
            plt.xlabel('Difference (Ontology2 - Ontology1)')
            plt.title('Metrics Difference Analysis')
            
            # Save the figure
            img_dir = os.path.join(output_path, 'img')
            os.makedirs(img_dir, exist_ok=True)
            filename = f"{comparison_data.ontology1_name}_vs_{comparison_data.ontology2_name}_metrics_difference.png"
            plt.savefig(os.path.join(img_dir, filename), format="png", bbox_inches='tight')
            plt.clf()
    
    def plot_subcharacteristics_comparison(
        self, comparison_data: ComparisonData, output_path: str
    ) -> None:
        """Create grouped bar charts for all characteristics
        
        Creates one grouped horizontal bar chart per characteristic, showing
        subcharacteristics values for both ontologies side-by-side.
        
        Args:
            comparison_data: ComparisonData object containing comparison data
            output_path: Base path for output directory
        """
        characteristics_comp = comparison_data.get_characteristics_comparison()
        img_dir = os.path.join(output_path, 'img')
        os.makedirs(img_dir, exist_ok=True)
        
        for characteristic, char_data in characteristics_comp.items():
            subchars = char_data['subcharacteristics']
            
            if not subchars:
                continue
            
            names = list(subchars.keys())
            values1 = [subchars[name][comparison_data.ontology1_name] for name in names]
            values2 = [subchars[name][comparison_data.ontology2_name] for name in names]
            
            # Create y positions with offset for grouping
            ypos = np.arange(len(names))
            bar_height = 0.35
            
            with plt.style.context(self.style):
                # Adjust figure height based on number of subcharacteristics
                if len(names) == 1:
                    plt.ylim(-1, 1)
                    bar_height = 0.6
                elif len(names) == 2:
                    plt.ylim(-1, 2)
                    bar_height = 0.8
                
                # Plot bars for both ontologies
                plt.barh(ypos - bar_height/2, values1, bar_height, 
                        color=self.ontology1_color, alpha=0.7, 
                        label=comparison_data.ontology1_name)
                plt.barh(ypos + bar_height/2, values2, bar_height, 
                        color=self.ontology2_color, alpha=0.7, 
                        label=comparison_data.ontology2_name)
                
                plt.yticks(ypos, names)
                plt.xlim([0, 5.5])
                
                # Add value annotations
                for i in range(len(names)):
                    plt.annotate(f'{values1[i]:.2f}', 
                               xy=(values1[i] + 0.1, ypos[i] - bar_height/2), 
                               textcoords='data', fontsize=8, va='center',
                               color=self.ontology1_color)
                    plt.annotate(f'{values2[i]:.2f}', 
                               xy=(values2[i] + 0.1, ypos[i] + bar_height/2), 
                               textcoords='data', fontsize=8, va='center',
                               color=self.ontology2_color)
                
                plt.title(f'{characteristic} Subcharacteristics Comparison')
                plt.legend(loc='best')
                
                # Save the figure
                filename = f"{comparison_data.ontology1_name}_vs_{comparison_data.ontology2_name}_{characteristic}_subcharacteristics_comparison.png"
                plt.savefig(os.path.join(img_dir, filename), format="png", bbox_inches='tight')
                plt.clf()