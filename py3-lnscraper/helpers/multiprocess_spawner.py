#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import Python's Modules
import os, sys, time, json
import multiprocessing

class multi_spawner():
    def __init__(self, workers=None, **options):
        self.force = options.pop('force', False)
        if workers is None:
            self.workers = 1
            self.cores = 1
        else:
            try:
                self.cores = multiprocessing.cpu_count()
            except Exception as excp:
                self.cores = 1
                print ('multiprocessing multi_spawner Could not detect System Core count, Default to 1.\n%s' % excp)
            if self.force:
                self.workers = workers
            else:
                self.workers = self.cores if workers > self.cores else workers
        self.Pool = multiprocessing.Pool(processes = self.workers)

    def spawn(self, worker_function, worker_args_collection):
        worker_results_collection = []
        if self.workers < 2:
            for worker_args_dict in worker_args_collection:
                worker_results_collection.append(
                    worker_function(**worker_args_dict)
                )
        else:
            result_queue = multiprocessing.Queue()
            batch_number = 0
            while len(worker_args_collection) > 0:
                batch_number += 1
                worker_queue = []
                batch_start = time.time()
                for _ in range(self.workers):
                    if len(worker_args_collection) > 0:
                        worker_args_raw = worker_args_collection.pop(0)
                        if isinstance(worker_args_raw, list):
                            worker_kwargs = {}
                            worker_args = []
                            for worker_arg_value in worker_args_raw:
                                if isinstance(worker_arg_value, dict):
                                    worker_kwargs.update(worker_arg_value)
                                elif isinstance(worker_arg_value, list):
                                    worker_args.extend(worker_arg_value)
                                else:
                                    worker_args.append(worker_arg_value)
                        else:
                            worker_args = []
                            worker_kwargs = worker_args_raw
                        worker_kwargs['queue'] = result_queue
                        worker_kwargs['batch'] = batch_number
                        # worker_args.append(result_queue)
                        worker_d = multiprocessing.Process(
                            target = worker_function, 
                            args = worker_args, 
                            kwargs = worker_kwargs, 
                        )
                        worker_queue.append(worker_d)
                        worker_d.start()
                    else:
                        break
                for worker_p in worker_queue:
                    worker_p.join()
                batch_end = time.time()
                print ('Batch %s Elapsed: [%s] Seconds' % (batch_number, int(batch_end - batch_start)))
            while not result_queue.empty():
                r = result_queue.get()
                print (r)
                worker_results_collection.append(r)
            result_queue.close()
        return worker_results_collection

