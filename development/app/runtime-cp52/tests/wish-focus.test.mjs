import test from 'node:test';
import assert from 'node:assert/strict';
import {liveWishFocus} from '../src/wish-focus.mjs';

test('A local paper wish offers its actual working person instead of the tree',()=>{
 const s={inputSession:{phase:'running',sceneId:'this-note',items:[{kind:'macro',target:'paper',action:'share'}]},sceneEvent:{id:'this-note',kind:'paper_share'},paperWorld:{eventId:'this-note',jobs:[{actor:'resident.customer_two',status:'running',context:{}}]}};
 assert.equal(liveWishFocus(s,'tree.lantern_tree'),'resident.customer_two');
 s.paperWorld.jobs[0].status='done';
 assert.equal(liveWishFocus(s,'tree.lantern_tree'),'tree.lantern_tree');
});
test('A spring task follows its worker while town-wide and finished wishes keep the chosen view',()=>{
 const s={inputSession:{phase:'running',sceneId:'spring-1',items:[{kind:'macro',target:'neighborhood',action:'spring'}]},sceneEvent:{id:'spring-1',kind:'spring'},neighborhoodWorld:{eventId:'spring-1',jobs:[{actor:'resident.gardener',status:'running',context:{}}]}};
 assert.equal(liveWishFocus(s,'tree.lantern_tree'),'resident.gardener');
 s.inputSession.items=[{kind:'macro',target:'occasion',action:'reunion'}];
 assert.equal(liveWishFocus(s,null),null);
 s.inputSession.items=[{kind:'macro',target:'neighborhood',action:'spring'}];s.inputSession.phase='done';
 assert.equal(liveWishFocus(s,'tree.lantern_tree'),'tree.lantern_tree');
});

test('The local music gathering offers the actual guitarist instead of an unrelated tree landmark',()=>{const s={inputSession:{phase:'running',sceneId:'music-1',items:[{kind:'macro',target:'street',action:'gather'}]},sceneEvent:{id:'music-1',kind:'music'}};assert.equal(liveWishFocus(s,null),'resident.musician');s.inputSession.phase='done';assert.equal(liveWishFocus(s,null),null);});
