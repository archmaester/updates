from tqdm import tqdm
import numpy as np
from operator import itemgetter 

class Trainer:
    
    def __init__(self, sess, model, data, settings, logger, plot ):
        
        self.plot = plot
        self.sess = sess
        self.model = model 
        self.data = data
        self.settings = settings
        self.logger = logger 
        self.z_dim = settings['latent_dim']
        self.t = 0 
    
    def train_epoch(self):
        
        loop = tqdm(range(self.settings['num_iter_per_epoch']))
#         loop = range(self.settings['num_iter_per_epoch'])
    
        for ii in loop:
            
            self.t = ii + 1
            
            loss_d, loss_g, loss_r, gen_sample = self.train_step()
            
            summaries_dict = { 'AutoEncoder/Decoder': loss_g, 'Discriminator': loss_d, 'AutoEncoder': loss_r }
            self.logger.summarize(ii, summaries_dict=summaries_dict)
            
            if ii % 10 == 0:
                
                self.plot.plot_sample(ii + 1, 6, gen_sample, self.model.channels)
            
            if ii == 0 :
                
                batch_x, batch_y = next(self.data.next_batch(self.settings["batch_size"]))
                self.plot.plot_sample(ii + 1, 6, batch_x, self.model.channels)
                
            
        self.model.save(self.sess)
        
    def train_step(self):

        G_r = self.settings['G_rounds']
        
        # Training AutoEncoder  
        batch_x, batch_y = next(self.data.next_batch(self.settings["batch_size"]))
        batch_z = np.random.uniform(-1, 1, size=(self.settings["batch_size"], self.z_dim, 1, 1))   
        
        feed_dict = {self.model.x_input: batch_x, self.model.z_input: batch_z}
        r_opt = self.sess.run(self.model.r_opt, feed_dict= feed_dict)

        # Training Discriminator 
        batch_x, batch_y = next(self.data.next_batch(self.settings["batch_size"]))
        batch_z = np.random.uniform(-1, 1, size=(self.settings["batch_size"], self.z_dim, 1, 1))   
        
        feed_dict = {self.model.x_input: batch_x, self.model.z_input: batch_z}
        d_opt = self.sess.run(self.model.d_opt, feed_dict= feed_dict)
        
        # Training Generator
        batch_x, batch_y = next(self.data.next_batch(self.settings["batch_size"]))
        batch_z = np.random.uniform(-1, 1, size=(self.settings["batch_size"], self.z_dim, 1, 1))   
        
        feed_dict = {self.model.x_input: batch_x, self.model.z_input: batch_z}
        g_opt = self.sess.run(self.model.g_opt, feed_dict= feed_dict)
                    
        loss_d = self.model.D_loss.eval(feed_dict = feed_dict, session = self.sess)
        loss_g = self.model.G_loss.eval(feed_dict = feed_dict, session = self.sess)
        loss_r = self.model.R_loss.eval(feed_dict = feed_dict, session = self.sess)
        gen_sample = self.sess.run(self.model.xg_input, feed_dict= feed_dict)
        
        return loss_d, loss_g, loss_r, gen_sample
    