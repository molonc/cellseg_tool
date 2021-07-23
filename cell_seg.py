from typing import Callable
import skimage.io as skio
import numpy as np
import click
import pandas as pd
from glob import glob
import os
import seg_metrics
import seg_methods 
import matplotlib.pyplot as plt
from typing import Callable

'''
Purpose:
========
The purpose of this application to to:
	1. Perform segmentation on MERFISH Images
	2. Extract segmentation performance metrics in comparison to a 1:1 ground truth image of the image
	3. Compare the segmentation performance metrics and put them in a graph. As well product files that will provide summary statstics to compare segmentation methods with

Purpose 1 and 2 will be capable of being run on a single image or a directory with the -d flag

Purpose 3 can be run on a single set of metrics from 2 or a list of output csvs

Usage:
========
Using python >3.6, you can run this tool with python cell_seg.py. --help with outline the subcommands and their uses
'''


@click.group()
def cli():
	pass


@cli.command('segment',help="Run a segmentation method in 'seg_methods' on a single image or a directory of TIFF images")
@click.option('-d',is_flag=True,help='DIRECTORY FLAG')
@click.argument('method',type=str)
@click.argument('image',type=click.Path(exists=True))
def segment(method,image,d):
	
	seg_func = funcPtr(method)
	
	if d:
		seg_fns = glob(os.path.join(image,'*.TIFF'))
		print(f'Found {len(seg_fns)} Images to segment...')
	else:
		seg_fns = list()
		seg_fns.append(image)

	print(f"Starting segmentation with {method} method")
	if d:
		m_folder_name = os.path.join(image,method)
	else:
		m_folder_name = os.path.join(os.path.dirname(image),method)
	
	if not os.path.exists(m_folder_name):
		os.makedirs(m_folder_name)

	for seg_idx, seg_fn in enumerate(seg_fns):
		print(seg_fn)
		im_fn = os.path.split(seg_fn)[1]

		click.echo(f"Segmentating {im_fn}")

		im2seg = skio.imread(seg_fn,plugin="tifffile")
		seg_result = seg_func(im2seg).astype(np.int16)
		m_file_name = os.path.join(m_folder_name,im_fn)
		skio.imsave(m_file_name,seg_result,plugin="tifffile")


@cli.command('calculate_metric',help="Calculate the metric(s) from seg_metrics on an image or a directory containing segmentation results as TIFF files.")
@click.option('-d',is_flag=True, help='DIRECTORY')
@click.argument('metric',nargs=-1,type=str)
@click.argument('seg_result',type=click.Path(exists=True))
@click.argument('seg_gt',type=click.Path(exists=True))
def calculate_metric(metric, seg_result,seg_gt, d):
	
	# * Put everything into list form
	if d:
		seg_results = glob(os.path.join(seg_result,'*.TIFF'))
		seg_gts = glob(os.path.join(seg_gt,'*.TIFF'))
	else:
		seg_results = list()
		seg_results.append(seg_result)
		seg_gts = list()
		seg_gts.append(seg_gt)

	# * Make sure the files in the directories are the same size
	if len(seg_results) != len(seg_gts):
		raise click.UsageError("The number of segment results is not equal to the number of ground truth images")
	metric_dict = dict()
	
	# * Get the function pointers for all the metrics
	for m in metric:
		metric_dict[m] = funcPtr(m,seg_metrics)
	metric_titles = metric_dict.keys()
	metric_vals = np.zeros((len(seg_results),len(metric)))

	# * Read in the segmentation results and the ground truth and run the metrics on them
	for seg_idx, seg_fn in enumerate(zip(seg_results,seg_gts)):
		seg_im = skio.imread(seg_fn[0],plugin="tifffile")
		seg_gt_im = skio.imread(seg_fn[1],plugin="tifffile")
	
		for m_idx,m in enumerate(metric_dict.keys()):
			metric_vals[seg_idx,m_idx] = metric_dict[m](seg_im,seg_gt_im)
	# * If this is a single image, just pop out the results into the terminal or if directory, save to a csv
	if d:
		df = pd.DataFrame(metric_vals)
		df.columns = metric_titles
		df['seg_results'] = seg_results
		df['seg_gt'] = seg_gts
		df.to_csv(os.path.join(seg_result,"seg_metrics.csv"), index=False)
	else:
		click.echo(metric_vals)



@cli.command('compare_metrics',help="Compare the output CSVs from calculate_metric")
@click.argument('csv',nargs=-1,type=click.Path(exists=True))
def compare_metrics(csv):
	# * Massage the inputs
	# if type(csv) != list:
	# 	csvs = list()
	# 	csvs.append(csv)
	# else:
	# 	csvs = csv
	csvs = csv
	n_csv = len(csvs)
	click.echo(f"Found {n_csv} CSVs")

	
	# * This will ensure we only compare metrics that exist across all the csvs 	
	metric_set = set()
	legend_names =list()
	df_list = list()
	for csv in csvs:
		print(csv)
		df = pd.read_csv(csv,sep=',')
		df_list.append(df)
		temp_set=df.columns.tolist()
		if len(metric_set)==0:
			metric_set=set(temp_set)
		metric_set = metric_set.intersection(temp_set)
		#For the plots later
		legend_names.append(os.path.basename(os.path.dirname(csv))) # Collecting names for the metrics

	metric_set.discard("seg_results")
	metric_set.discard("seg_gt")
	
	for im, m in enumerate(metric_set):
		f = plt.figure()
		df = pd.DataFrame()	
		for c in np.arange(len(df_list)):
			df = pd.concat([df,df_list[c][m]],axis=1)

		# Use a ridgeplot in the future?
		df.plot()
		plt.title(m+' Comparison')
		plt.xlabel("Image number")
		plt.ylabel(m)
		plt.legend(legend_names)
		plt.savefig('./'+m+'_comparison.png')
		# Output summary stats for comparisons
		summ_stats = df.describe()
		
		summ_stats.columns =  [summ_stats.columns[ic]+'_'+legend_names[ic-1] for ic in range(len(summ_stats.columns))]
		summ_stats.to_csv('./'+m+'_summ_stats.csv')


def funcPtr(method:str,module=seg_methods)->Callable:
	"""This function gets a function pointer based on the name of the function. 

	Args:
		method (str): The name of the function to import from the module
		module (optional): Module to get the function pointer from. Defaults to seg_methods.

	Returns:
		Callable: The return can be called with the signature of the function with the name 'method' in the module 'module'
	"""
	
	mymodule = getattr(module, method)
	myfunction = getattr(module, method)
	
	return myfunction



if __name__ == '__main__':
	cli()
	